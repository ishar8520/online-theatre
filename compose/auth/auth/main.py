from __future__ import annotations

import logging.config

from fastapi import FastAPI

from .core import LOGGING

logging.config.dictConfig(LOGGING)

app = FastAPI(
    title='Auth service',
    description='Authentication & authorization service',
    docs_url='/auth/api/openapi',
    openapi_url='/auth/api/openapi.json',
)
