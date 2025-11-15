from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import chat, documents, bots, analytics
from app.api import auth_db as auth  # Usar PostgreSQL

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API del chatbot RAG multi-tenant con gestión de bots y analytics"
)

# Configurar límite de tamaño de archivo (50MB)
app.router.redirect_slashes = False

# CORS configurado para permitir embeddings en cualquier sitio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas principales
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(bots.router, prefix="/bots", tags=["Bots"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


@app.get("/", tags=["Health"])
def root():
    """Endpoint de health check"""
    return {
        "message": "Chatbot RAG API funcionando",
        "version": "1.0.0",
        "env": settings.APP_ENV,
        "features": [
            "JWT Authentication & Authorization",
            "Multi-tenant bot management",
            "RAG with ChromaDB",
            "PDF, DOCX, TXT support",
            "Analytics and metrics",
            "Customizable prompts per bot",
            "Role-based access control (RBAC)"
        ]
    }


@app.get("/health", tags=["Health"])
def health():
    """Endpoint detallado de health check"""
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "version": "1.0.0"
    }
