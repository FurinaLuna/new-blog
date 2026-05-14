from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://blog:blog_secret@localhost:5432/blog"
    database_url_sync: str = "postgresql://blog:blog_secret@localhost:5432/blog"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # Upload
    upload_dir: str = "uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    # LLM (OpenAI-compatible)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.deepseek.com"
    openai_model: str = "deepseek-v4-flash"

    # Embedding (separate from LLM, DeepSeek doesn't provide embeddings)
    embedding_api_key: str = ""
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: str = "http://localhost:5173"
    site_url: str = "http://localhost:5173"
    site_name: str = "My Blog"
    site_description: str = "Personal blog RSS feed"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
