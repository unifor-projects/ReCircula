import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # CORS – comma-separated list of allowed origins; '*' only in development
    CORS_ORIGINS: str = "*"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/recircula_db"

    # JWT – SECRET_KEY must be set in production via environment variable
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Email (SMTP) – leave SMTP_HOST empty to disable email sending
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@recircula.app"
    SMTP_TLS: bool = True

    # Frontend base URL used in e-mail links
    FRONTEND_URL: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
