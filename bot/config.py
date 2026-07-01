from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., min_length=40)
    ADMIN_IDS: list[int] = []
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    WEBAPP_URL: str
    CRM_URL: str
    PAYMENT_PROVIDER_TOKEN: str = ""
    SECRET_KEY: str = Field(..., min_length=32)
    WEBHOOK_SECRET: str = Field(default="webhook-secret-change-me")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
