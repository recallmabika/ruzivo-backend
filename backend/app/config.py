from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Ruzivo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str

    DATABASE_URL: str
    REDIS_URL: str

    HF_TOKEN: str

    LLM_MODEL_ID: str
    ASR_MODEL_ID: str
    TTS_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    RAG_DATASET_ID: str

    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: str
    ALLOWED_DOC_TYPES: str

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
