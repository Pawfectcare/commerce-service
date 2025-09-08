from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Commerce Service"
    APP_VERSION: str = "1.0"
    DATABASE_URL: str
    PAYMENT_PROVIDER_KEY: str
    JWT_SECRET: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
