from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "River Connect"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://admin:admin123@localhost:5432/vessel_system"
    database_url_sync: str = "postgresql://admin:admin123@localhost:5432/vessel_system"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "river-connect-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
