from __future__ import annotations

import logging.config

from fastapi import FastAPI

from .core import LOGGING

logging.config.dictConfig(LOGGING)

base_api_prefix = '/api'
app = FastAPI(
    title='Notifications queue service',
    description='API for queueing notifications.',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
)


@app.get(f'{base_api_prefix}/_health')
async def healthcheck() -> dict:
    return {}
