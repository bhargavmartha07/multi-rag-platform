from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Enterprise RAG Platform"

    APP_VERSION: str = "1.0.0"

    API_PREFIX: str = "/api/v1"

    APP_ENV: str = "development"

    DATABASE_URL: str

    JWT_SECRET_KEY: str

    JWT_ALGORITHM: str

    REDIS_URL: str

    QDRANT_URL: str

    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()