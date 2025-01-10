from __future__ import annotations

from fastapi import FastAPI


app = FastAPI(
    title='Auth service',
    description='Authentication & authorization service',
    docs_url='/auth/api/openapi',
    openapi_url='/auth/api/openapi.json',
)
