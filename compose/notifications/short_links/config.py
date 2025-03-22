from pydantic_settings import BaseSettings, SettingsConfigDict

SHORT_LINK_TTL = 300

class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')
    
    host: str
    port: int
    
class Settings(BaseSettings):
    redis: RedisConfig = RedisConfig()
    

settings = Settings()
