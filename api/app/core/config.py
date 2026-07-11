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

    LLM_PROVIDER: str = "ollama"

    OPENAI_API_KEY: str = "sk-placeholder"

    GROQ_API_KEY: str = ""

    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434/v1"

    LLM_MODEL: str = "llama3.2"

    EMBEDDING_PROVIDER: str = "ollama"

    EMBEDDING_MODEL: str = "nomic-embed-text"

    EMBEDDING_DIMENSIONS: int = 768

    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    OPENAI_EMBEDDING_DIMENSIONS: int = 1536

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
