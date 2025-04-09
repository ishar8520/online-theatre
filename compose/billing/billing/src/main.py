from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .api.v1.endpoints import payment

base_api_prefix = '/billing/api'
app = FastAPI(
    title='Billing service',
    description='Service for purchase subscribe, movies and emoji',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    default_response_class=JSONResponse,
)


@app.get(f'{base_api_prefix}/_health')
async def healthcheck():
    return {}


notify_api_prefix = f'{base_api_prefix}/v1'

app.include_router(
    payment.router,
    prefix=f'{notify_api_prefix}/payment',
    tags=['payment']
)
