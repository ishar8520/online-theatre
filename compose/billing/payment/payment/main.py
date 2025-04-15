from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from payment.api.v1.endpoints import yoomoney, yoomoney_test_callback

base_api_prefix = '/payment/api'

app = FastAPI(
    title='Payment service',
    description='Payment service for execute pay via external; service',
    docs_url=f'{base_api_prefix}/openapi',
    openapi_url=f'{base_api_prefix}/openapi.json',
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

app.include_router(yoomoney.router, prefix=f'{base_prefix_url}/yoomoney')
app.include_router(yoomoney_test_callback.router, prefix=f'{base_prefix_url}/yoomoney')
