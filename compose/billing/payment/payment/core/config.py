from pydantic_settings import BaseSettings, SettingsConfigDict

class YooMoneyConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='yoomoney_')
    
    client_id: str
    secret: str
    redirect_uri: str
    receiver_account: str
    
class Settings(BaseSettings):
    yoomoney: YooMoneyConfig = YooMoneyConfig()
    
settings = Settings()