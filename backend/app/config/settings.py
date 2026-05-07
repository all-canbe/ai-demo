from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "DocAI"
    APP_NAME: str = "DocAI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    API_PREFIX: str = "/api"

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/docai"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 3600

    JWT_SECRET_KEY: str = "change-this-to-a-secure-secret-key-at-least-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSION: int = 1536
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE: int = 52428800
    ALLOWED_FILE_TYPES: list[str] = [
        "pdf", "docx", "doc", "png", "jpg", "jpeg", "txt", "md", "html"
    ]
    TESSERACT_PATH: str = "/usr/bin/tesseract"
    MILVUS_COLLECTION: str = "document_chunks"

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
