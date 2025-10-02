from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Camwater PAY+"
    APP_ENV: str = "dev"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DATABASE_URL: str = "sqlite+aiosqlite:///./camwater.db"
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MIN: int = 1440
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    FLW_SECRET_KEY: str | None = None
    FLW_WEBHOOK_SECRET: str | None = None
    CURRENCY: str = "XAF"
    TUI_EXP_MINUTES: int = 15
    TUI_SIGNING_SECRET: str
    LUNA_BASE_URL: str | None = None
    LUNA_USERNAME: str | None = None
    LUNA_PASSWORD: str | None = None
    LUNA_CARD_PROFILE_JSON: str | None = None
    CARD_CRYPTO_PROVIDER: str = "mock"  # mock|hsm|disabled
    ENABLE_REMOTE_APPLY_FALLBACK: bool = False
    class Config: env_file = ".env"

settings = Settings()
