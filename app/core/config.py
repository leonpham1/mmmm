from pydantic import VERSION
from pydantic_settings import BaseSettings, SettingsConfigDict

class SystemSettings(BaseSettings):
    PROJECT_NAME: str = "mmmm App"
    VERSION: str = "0.1.0"
    
    model_config = SettingsConfigDict(env_file=".env")

system_settings = SystemSettings()