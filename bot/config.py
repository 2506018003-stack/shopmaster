from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field, validator
import json
import os

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., min_length=40)
    ADMIN_IDS: list[int] = []
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    WEBAPP_URL: str = "https://telegram-autoposter-z0dw.onrender.com/miniapp"
    CRM_URL: str = "https://telegram-autoposter-z0dw.onrender.com/crm"
    PAYMENT_PROVIDER_TOKEN: str = ""
    SECRET_KEY: str = Field(default="change-me-please-now-immediately-32-chars-min", min_length=32)
    WEBHOOK_SECRET: str = Field(default="webhook-secret-change-me")
    DEBUG: bool = False

    @validator('ADMIN_IDS', pre=True, always=True)
    def parse_admin_ids(cls, v):
        """Парсит ADMIN_IDS из разных форматов: int, str, JSON list, CSV"""
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith('['):
                try:
                    return json.loads(v)
                except:
                    pass
            try:
                return [int(x.strip()) for x in v.split(',') if x.strip()]
            except:
                try:
                    return [int(v)]
                except:
                    return []
        return v or []

    @validator('DATABASE_URL', pre=True, always=True)
    def parse_database_url(cls, v):
        """Защита от пустой строки + авто-конвертация postgres:// → postgresql+asyncpg://"""
        if not v or str(v).strip() == '':
            internal = os.getenv('DATABASE_INTERNAL_URL', '')
            if internal:
                return internal.replace('postgres://', 'postgresql+asyncpg://').replace('postgresql://', 'postgresql+asyncpg://')
            raise ValueError("DATABASE_URL is required. Set it in Render Environment variables.")
        url = str(v).strip()
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql+asyncpg://', 1)
        elif url.startswith('postgresql://') and 'asyncpg' not in url:
            url = url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return url

    @validator('SECRET_KEY', pre=True, always=True)
    def validate_secret_key(cls, v):
        """Генерирует ключ если пустой (dev), строгое требование (production)"""
        if not v or str(v).strip() == '' or len(str(v)) < 32:
            if os.getenv('RENDER', '').lower() == 'true' or os.getenv('PRODUCTION', '').lower() == 'true':
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters. Generate: openssl rand -hex 32"
                )
            import secrets
            generated = secrets.token_hex(32)
            print(f"⚠️  WARNING: Auto-generated SECRET_KEY for dev: {generated[:16]}...")
            return generated
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = ""

settings = Settings()
