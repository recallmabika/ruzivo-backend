from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Ruzivo"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "postgresql://ruzivo_user:change-me@localhost:5432/ruzivo_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Model paths
    llm_model_path: str = "models/llm/shona-mistral-7b"
    asr_model_path: str = "models/asr/shona-whisper-small"
    tts_model_path: str = "models/tts/shona-voice"

    # ChromaDB
    chroma_persist_dir: str = "rag/knowledge_base/chroma_store"
    chroma_collection: str = "ruzivo_kb"

    # HuggingFace
    hf_token: str = ""

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    allowed_origins: str = "http://localhost:8081,http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
