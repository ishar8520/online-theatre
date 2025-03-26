from fastapi import FastAPI
from config import settings
from api import router

base_api_prefix = '/websocket/api'

app = FastAPI(title=settings.APP_NAME,
              description='Websocket service.',
              docs_url=f'{base_api_prefix}/openapi',
              openapi_url=f'{base_api_prefix}/openapi.json')

app.include_router(
    router,
    prefix=base_api_prefix,
    tags=['websocket']
)
