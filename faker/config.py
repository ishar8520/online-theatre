from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    database: str
    username: str
    password: str
    host: str = 'postgresql'
    port: int = 5432

    class Config:
        env_prefix = 'POSTGRESQL_'
