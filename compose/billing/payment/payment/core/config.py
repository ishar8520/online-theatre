from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')
    
    host: str
    port: int

class RabbitConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='rabbitmq_')
    
    username: str
    password: str
    host: str
    port: int
    
    @property
    def url(self) -> str:
        return f'amqp://{self.username}:{self.password}@{self.host}:{self.port}'

class YooMoneyConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='yoomoney_')
    
    client_id: str
    secret: str
    redirect_uri: str
    receiver_account: str
    
class Settings(BaseSettings):
    redis: RedisConfig = RedisConfig()
    rabbitmq: RabbitConfig = RabbitConfig()
    yoomoney: YooMoneyConfig = YooMoneyConfig()
    
settings = Settings()
