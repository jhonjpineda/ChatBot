from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.chat_service import get_chat_service

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
