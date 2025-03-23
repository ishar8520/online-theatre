from pydantic_settings import BaseSettings


class FastApiSettings(BaseSettings):
    APP_NAME: str = 'WebSocket Service'
    HOST: str = '0.0.0.0'
    PORT: int = 8000


settings = FastApiSettings()