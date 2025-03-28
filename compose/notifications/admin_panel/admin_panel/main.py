from __future__ import annotations

import logging.config
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

import httpx
import sentry_sdk
from fastapi import FastAPI, Request, Response, status
from fastapi_pagination.utils import disable_installed_extensions_check
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
from admin_panel.scheduler import scheduler_cron

from .api.v1 import admin_notification, template, scheduler
from .core import LOGGING, settings


disable_installed_extensions_check()
logging.config.dictConfig(LOGGING)

if settings.sentry.enable_sdk:
    sentry_sdk.init(
        dsn=settings.sentry.dsn,
        traces_sample_rate=settings.sentry.traces_sample_rate,
        profiles_sample_rate=settings.sentry.profiles_sample_rate,
        enable_tracing=settings.sentry.enable_tracing,
    )
    sentry_sdk.set_tag("service_name", "admin-panel-service")


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
    scheduler_cron.start()

    async with (
        httpx.AsyncClient() as httpx_client,
    ):
        yield {
            'httpx_client': httpx_client,
        }
    scheduler_cron.shutdown()


base_api_prefix = '/admin_panel/api'
app = FastAPI(
    title=settings.project.name,
    description='Administrative panel for project managers to create mailings.',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan,
)
FastAPIInstrumentor.instrument_app(
    app,
    excluded_urls=f'{base_api_prefix}/_health',
    http_capture_headers_server_request=['X-Request-Id'],
)


@app.middleware('http')
async def check_request_id(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    if settings.otel.enabled and settings.otel.request_id_required:
        request_id = request.headers.get('X-Request-Id')

        if not request_id:
            return JSONResponse({
                'detail': 'X-Request-Id is required',
            }, status_code=status.HTTP_400_BAD_REQUEST)

    return await call_next(request)


@app.get(f'{base_api_prefix}/_health')
async def healthcheck() -> dict:
    return {}


admin_notification_prefix = f'{base_api_prefix}/v1'

app.include_router(
    admin_notification.router,
    prefix=f'{admin_notification_prefix}/admin_notification',
    tags=['admin_notification'],
)
app.include_router(
    template.router,
    prefix=f'{admin_notification_prefix}/template',
    tags=['template'],
)
app.include_router(
    scheduler.router,
    prefix=f'{admin_notification_prefix}/scheduler',
    tags=['scheduler']
)
