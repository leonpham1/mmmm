from pydantic_settings import BaseSettings, SettingsConfigDict

class SystemSettings(BaseSettings):
    PROJECT_NAME: str = "mmmm App"
    
    model_config = SettingsConfigDict(env_file=".env")

system_settings = SystemSettings()