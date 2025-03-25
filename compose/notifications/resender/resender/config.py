from pydantic_settings import BaseSettings, SettingsConfigDict

class RabbitConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='rabbitmq_')
    
    username: str
    password: str
    host: str
    port: int
    
    @property
    def url(self) -> str:
        return f'amqp://{self.username}:{self.password}@{self.host}:{self.port}'

class Settings(BaseSettings):
    rabbitmq: RabbitConfig = RabbitConfig()

settings = Settings()