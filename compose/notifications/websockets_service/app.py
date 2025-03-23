from fastapi import FastAPI
from config import settings
from api import router

app = FastAPI(title=settings.APP_NAME)

app.include_router(router)