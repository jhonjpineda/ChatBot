from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import chat
from app.api import documents  # <-- nuevo

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="API del chatbot RAG multisitio"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])


@app.get("/")
def root():
    return {"message": "Chatbot API funcionando", "env": settings.APP_ENV}
