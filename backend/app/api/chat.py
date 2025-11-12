from fastapi import APIRouter
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
