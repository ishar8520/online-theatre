from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from payment.api.v1.endpoints import yoomoney, yoomoney_test_callback
from payment.services.rabbitmq import rabbitmq

base_api_prefix = '/payment/api'


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq.connect()
    yield
    await rabbitmq.close()

app = FastAPI(
    title='Payment service',
    description='Payment service for execute pay via external; service',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "https://yoomoney.ru"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

base_prefix_url = f'{base_api_prefix}/v1'

@app.get(f'{base_api_prefix}/_health')
async def healthcheck():
    return {}

app.include_router(yoomoney.router_ex, prefix=f'{base_prefix_url}/yoomoney', tags=['external methods'])
app.include_router(yoomoney.router_in, prefix=f'{base_prefix_url}/yoomoney', tags=['internal methods'])
app.include_router(yoomoney_test_callback.router, prefix=f'{base_prefix_url}/yoomoney', tags=['test methods'])
