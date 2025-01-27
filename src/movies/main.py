from __future__ import annotations

import logging.config
from collections.abc import AsyncGenerator, Callable, Awaitable
from contextlib import asynccontextmanager

import elasticsearch
import redis.asyncio as redis
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.jaeger import JaegerPropagator
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from .api.v1.endpoints import films, genres, persons
from .core import settings, LOGGING

logging.config.dictConfig(LOGGING)


def configure_otel() -> None:
    if not settings.otel.enabled:
        return

    resource = Resource(attributes={
        SERVICE_NAME: settings.otel.service_name,
    })
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    span_exporter = OTLPSpanExporter(endpoint=settings.otel.exporter_otlp_http_endpoint)
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)

    set_global_textmap(CompositePropagator([
        TraceContextTextMapPropagator(),
        W3CBaggagePropagator(),
        JaegerPropagator(),
    ]))


@asynccontextmanager
async def lifespan(_app) -> AsyncGenerator[dict]:
    configure_otel()

    async with (
        redis.Redis(host=settings.redis.host, port=settings.redis.port) as redis_client,
        elasticsearch.AsyncElasticsearch(settings.elasticsearch.url) as elasticsearch_client,
    ):
        yield {
            'redis_client': redis_client,
            'elasticsearch_client': elasticsearch_client,
        }


app = FastAPI(
    title=settings.project.name,
    description=(
        'Backend service that returns films, persons (actors, writers, directors) '
        'and genres of films by uuid.'
    ),
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan,
)
FastAPIInstrumentor.instrument_app(app, http_capture_headers_server_request=['X-Request-Id'])


@app.middleware('http')
async def check_request_id(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    if settings.otel.enabled and settings.otel.request_id_required:
        request_id = request.headers.get('X-Request-Id')

        if not request_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='X-Request-Id is required',
            )

    return await call_next(request)


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
