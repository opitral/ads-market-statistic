from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_BASE_URL: str
    API_ID: int
    API_HASH: str
    GENERAL_CHANNEL_TELEGRAM_ID: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()
