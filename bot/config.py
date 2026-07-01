from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field, validator
import json
import os

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., min_length=40)
    ADMIN_IDS: list[int] = []
    DATABASE_URL: str = "sqlite+aiosqlite:///./shopmaster.db"
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    WEBAPP_URL: str = "https://telegram-autoposter-z0dw.onrender.com/miniapp"
    CRM_URL: str = "https://telegram-autoposter-z0dw.onrender.com/crm"
    PAYMENT_PROVIDER_TOKEN: str = ""
    SECRET_KEY: str = Field(default="change-me-please-now-immediately-32-chars-min", min_length=32)
    WEBHOOK_SECRET: str = Field(default="webhook-secret-change-me")
    DEBUG: bool = False

    @validator('ADMIN_IDS', pre=True, always=True)
    def parse_admin_ids(cls, v):
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
        if not v or str(v).strip() == '':
            print("⚠️  WARNING: DATABASE_URL empty, using SQLite fallback. For production, set postgresql+asyncpg:// URL")
            return "sqlite+aiosqlite:///./shopmaster.db"
        url = str(v).strip()
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql+asyncpg://', 1)
        elif url.startswith('postgresql://') and 'asyncpg' not in url:
            url = url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return url

    @validator('SECRET_KEY', pre=True, always=True)
    def validate_secret_key(cls, v):
        if not v or str(v).strip() == '' or len(str(v)) < 32:
            import secrets
            generated = secrets.token_hex(32)
            print(f"⚠️  Auto-generated SECRET_KEY: {generated[:16]}...")
            return generated
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = ""

settings = Settings()
