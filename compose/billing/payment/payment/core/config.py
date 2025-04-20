# mypy: disable-error-code=call-arg
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    """Конфигурация базового URL основного сервиса."""

    model_config = SettingsConfigDict(env_prefix='service_')

    url: str


class ShortlinkConfig(BaseSettings):
    """Конфигурация сервиса сокращения ссылок."""

    model_config = SettingsConfigDict(env_prefix='short_link_')

    url: str


class RedisConfig(BaseSettings):
    """Конфигурация подключения к Redis."""

    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str
    port: int


class RabbitConfig(BaseSettings):
    """Конфигурация подключения к серверу RabbitMQ."""

    model_config = SettingsConfigDict(env_prefix='rabbitmq_')

    username: str
    password: str
    host: str
    port: int

    @property
    def url(self) -> str:
        """Формирует URL для подключения к RabbitMQ."""
        return f'amqp://{self.username}:{self.password}@{self.host}:{self.port}'


class YooMoneyConfig(BaseSettings):
    """Конфигурация для интеграции с API YooMoney."""

    model_config = SettingsConfigDict(env_prefix='yoomoney_')

    client_id: str
    secret: str
    redirect_uri: str
    receiver_account: str
    token_account: str


class Settings(BaseSettings):
    """Основная конфигурация приложения, объединяющая все сервисы."""

    service: ServiceConfig = ServiceConfig()
    short_link: ShortlinkConfig = ShortlinkConfig()
    redis: RedisConfig = RedisConfig()
    rabbitmq: RabbitConfig = RabbitConfig()
    yoomoney: YooMoneyConfig = YooMoneyConfig()


settings = Settings()
