# D:\2025\ChatBot\backend\app\llm_providers\factory.py

from app.core.config import settings
from app.llm_providers.ollama_client import OllamaClient

def get_llm_client():
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        # importación perezosa para no requerir openai cuando no se usa
        from app.llm_providers.openai_client import OpenAIClient
        return OpenAIClient(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )

    # por defecto usamos ollama
    return OllamaClient(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL
    )
