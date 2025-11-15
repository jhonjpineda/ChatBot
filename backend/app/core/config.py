# D:\2025\ChatBot\backend\app\core\config.py

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(extra='allow', env_file='.env', env_file_encoding='utf-8')

    APP_NAME: str = "Chatbot RAG"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # proveedor de LLM: "ollama" o "openai"
    LLM_PROVIDER: str = "ollama"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # PostgreSQL
    DATABASE_URL: str = ""
    USE_DATABASE: bool = False

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
