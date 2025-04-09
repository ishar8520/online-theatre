from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='payment_redis_')

    host: str
    port: int

class YooMoneyConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='yoomoney_')
    
    client_id: str
    secret: str
    redirect_uri: str
    
class Settings(BaseSettings):
    yoomoney: YooMoneyConfig = YooMoneyConfig()
    redis: RedisConfig = RedisConfig()
    
settings = Settings()