from pydantic_settings import BaseSettings, SettingsConfigDict

class ServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='service_')
    
    url: str

class ShortlinkConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='short_link_')
    
    url: str

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
    token_account: str
    
class Settings(BaseSettings):
    service: ServiceConfig = ServiceConfig()
    short_link: ShortlinkConfig = ShortlinkConfig()
    redis: RedisConfig = RedisConfig()
    rabbitmq: RabbitConfig = RabbitConfig()
    yoomoney: YooMoneyConfig = YooMoneyConfig()
    
settings = Settings()
