"""
API de chat con RAG preciso y streaming de respuestas.
Endpoints para chatear con bots usando Server-Sent Events (SSE).
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.services.chat_service_enhanced import get_chat_service_enhanced
from app.services.retriever_service import RetrieverService

router = APIRouter()


class ChatRequest(BaseModel):
    """Request para chat"""
    question: str
    bot_id: str = "default"


class ChatResponse(BaseModel):
    """Response para chat sin streaming"""
    answer: str
    sources: list
    bot_config: dict
    warning: Optional[str] = None


@router.post("/", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    """
    Endpoint de chat sin streaming (respuesta completa de una vez).

    Características:
    - Usa RAG preciso con strict_mode
    - Filtra por threshold de similitud
    - Retorna fallback si no hay docs relevantes
    - Limita número de fuentes con max_sources

    Returns:
        ChatResponse con answer, sources y bot_config
    """
    chat_service = get_chat_service_enhanced()

    try:
        result = chat_service.answer(payload.question, payload.bot_id)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/stream")
def chat_stream_endpoint(payload: ChatRequest):
    """
    Endpoint de streaming que devuelve la respuesta del chatbot en tiempo real.

    **Características:**
    - Usa Server-Sent Events (SSE) para streaming
    - Chunks progresivos palabra por palabra
    - RAG preciso con strict_mode
    - Fallback personalizado si no hay docs

    **Formato de respuesta (SSE):**

    ```
    data: {"type": "metadata", "sources": [...], "bot_config": {...}}

    data: {"type": "chunk", "content": "Hola"}

    data: {"type": "chunk", "content": " mundo"}

    data: {"type": "done"}
    ```

    **O si no hay docs relevantes (strict_mode):**

    ```
    data: {"type": "metadata", "sources": [], "bot_config": {...}}

    data: {"type": "chunk", "content": "Lo siento, no tengo información..."}

    data: {"type": "done", "fallback": true}
    ```

    **Headers necesarios en el cliente:**
    ```javascript
    const eventSource = new EventSource('/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({question, bot_id})
    });
    ```

    **Integración frontend:**
    Ver STREAMING_GUIDE.md para ejemplos completos.
    """
    chat_service = get_chat_service_enhanced()

    try:
        return StreamingResponse(
            chat_service.answer_stream(payload.question, payload.bot_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Desactivar buffering en nginx
                "Access-Control-Allow-Origin": "*",  # CORS para desarrollo
            }
        )

    except ValueError as e:
        # Retornar error en formato SSE
        import json
        error_stream = [
            f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        ]
        return StreamingResponse(
            iter(error_stream),
            media_type="text/event-stream"
        )


@router.get("/debug-retrieval")
def debug_retrieval(
    query: str = Query(..., description="Pregunta a buscar"),
    bot_id: str = Query(default="default", description="ID del bot"),
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Threshold de similitud"),
    k: int = Query(default=5, ge=1, le=20, description="Número de resultados")
):
    """
    Endpoint de debug para el sistema de retrieval.

    Muestra qué chunks se recuperan para una pregunta, incluyendo:
    - Texto de cada chunk
    - Similarity score
    - Metadata
    - Si pasa el threshold o no

    Útil para:
    - Ajustar el threshold óptimo
    - Ver qué documentos se están usando
    - Debuggear por qué no encuentra info relevante
    """
    retriever = RetrieverService()

    # Buscar con o sin threshold
    results = retriever.search(
        query=query,
        bot_id=bot_id,
        k=k,
        threshold=threshold
    )

    return {
        "query": query,
        "bot_id": bot_id,
        "threshold_used": threshold,
        "total_chunks_found": len(results),
        "chunks": [
            {
                "index": i + 1,
                "similarity": chunk.get("similarity"),
                "distance": chunk.get("distance"),
                "passes_threshold": chunk.get("similarity", 0) >= threshold if threshold else True,
                "text_preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                "full_text": chunk["text"],
                "metadata": chunk.get("metadata", {}),
            }
            for i, chunk in enumerate(results)
        ],
        "recommendations": {
            "avg_similarity": sum(c.get("similarity", 0) for c in results) / len(results) if results else 0,
            "min_similarity": min(c.get("similarity", 0) for c in results) if results else 0,
            "max_similarity": max(c.get("similarity", 0) for c in results) if results else 0,
            "suggested_threshold": 0.3 if not results or sum(c.get("similarity", 0) for c in results) / len(results) < 0.4 else 0.5
        }
    }


@router.post("/test-strict-mode")
def test_strict_mode(
    question: str = Query(..., description="Pregunta de prueba"),
    bot_id: str = Query(default="default", description="ID del bot")
):
    """
    Endpoint de testing para verificar strict_mode.

    Prueba qué pasa cuando:
    - Hay docs relevantes → Responde con ellos
    - NO hay docs relevantes → Retorna fallback

    Útil para verificar configuración antes de producción.
    """
    chat_service = get_chat_service_enhanced()

    try:
        result = chat_service.answer(question, bot_id)

        return {
            "question": question,
            "bot_id": bot_id,
            "answer": result["answer"],
            "sources_found": len(result["sources"]),
            "is_fallback": "warning" in result,
            "bot_config": result["bot_config"],
            "sources": [
                {
                    "similarity": s.get("similarity"),
                    "text_preview": s["text"][:100] + "..."
                }
                for s in result["sources"]
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
