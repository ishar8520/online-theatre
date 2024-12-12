from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    database: str
    username: str
    password: str
    host: str = 'localhost'
    port: int = 6432

    class Config:
        env_prefix = 'POSTGRESQL_'
