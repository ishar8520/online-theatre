from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.v1.endpoints import messages, events


base_api_prefix = '/notification/api'
app = FastAPI(
    title='Notifications hub',
    description='Service accept notification requests and send to rabbitMQ',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    default_response_class=JSONResponse,
)


@app.get(f'{base_api_prefix}/_health')
async def healthcheck():
    return {}


notify_api_prefix = f'{base_api_prefix}/v1'

app.include_router(
    events.router,
    prefix=f'{notify_api_prefix}/events',
    tags=['events']
)

app.include_router(
    messages.router,
    prefix=f'{notify_api_prefix}/messages',
    tags=['messages']
)
