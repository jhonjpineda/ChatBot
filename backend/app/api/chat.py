from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.chat_service import get_chat_service
from app.services.retriever_service import RetrieverService

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    bot_id: str = "default"

@router.post("/")
def chat_endpoint(payload: ChatRequest):
    chat_service = get_chat_service()
    result = chat_service.answer(payload.question, payload.bot_id)
    return result

@router.post("/stream")
def chat_stream_endpoint(payload: ChatRequest):
    """
    Endpoint de streaming que devuelve la respuesta del chatbot en tiempo real.
    Usa Server-Sent Events (SSE) para enviar chunks progresivamente.
    """
    chat_service = get_chat_service()

    return StreamingResponse(
        chat_service.answer_stream(payload.question, payload.bot_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Desactivar buffering en nginx
        }
    )

@router.get("/debug-retrieval")
def debug_retrieval(
    query: str = Query(..., description="Pregunta a buscar"),
    bot_id: str = Query(default="default", description="ID del bot")
):
    """
    Endpoint temporal para debuggear el retrieval.
    Muestra qué chunks se recuperan para una pregunta.
    """
    retriever = RetrieverService()
    results = retriever.search(query, bot_id=bot_id)

    return {
        "query": query,
        "bot_id": bot_id,
        "total_chunks": len(results),
        "chunks": [
            {
                "text_preview": chunk["text"][:300] + "...",
                "full_text": chunk["text"],
                "metadata": chunk.get("metadata", {}),
                "distance_score": chunk.get("score")
            }
            for chunk in results
        ]
    }
