from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "MMMM App"
    ZALO_OA_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()