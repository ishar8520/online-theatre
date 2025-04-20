from pydantic_settings import BaseSettings, SettingsConfigDict

class RabbitConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='rabbitmq_')
    
    username: str
    password: str
    host: str
    port: int
    queue_name: str
    
    @property
    def url(self) -> str:
        return f'amqp://{self.username}:{self.password}@{self.host}:{self.port}'

class BillingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='billing_service_')
    
    host: str
    port: int

class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')
    
    host: str
    port: int
    login: str
    password: str
    
class SettingsConfig(BaseSettings):
    rabbitmq: RabbitConfig = RabbitConfig()
    billing: BillingConfig = BillingConfig()
    auth: AuthConfig = AuthConfig()
    
settings = SettingsConfig()