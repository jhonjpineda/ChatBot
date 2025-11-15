"""
Servicio de chat mejorado con RAG preciso y configuración avanzada.
Incluye strict_mode, threshold filtering y fallback responses.
"""
import time
from typing import Dict, Any, Generator
from app.services.retriever_service import RetrieverService
from app.services.bot_service import BotService
from app.services.analytics_service import AnalyticsService
from app.llm_providers.factory import get_llm_client


class ChatServiceEnhanced:
    """
    Servicio de chat con RAG preciso.

    Características:
    - strict_mode: Solo responde con información de documentos
    - threshold filtering: Filtra chunks por similitud mínima
    - fallback response: Respuesta personalizada cuando no hay info
    - max_sources: Limita número de fuentes en contexto
    """

    def __init__(self, llm_client, retriever: RetrieverService, bot_service: BotService, analytics_service: AnalyticsService):
        self.llm = llm_client
        self.retriever = retriever
        self.bot_service = bot_service
        self.analytics = analytics_service

    def answer(self, user_question: str, bot_id: str) -> Dict[str, Any]:
        """
        Responde una pregunta usando RAG preciso.

        Returns:
            Dict con answer, sources y bot_config
        """
        start_time = time.time()
        success = True
        error_msg = None
        answer = ""
        context_chunks = []

        try:
            # 1. Obtener configuración del bot
            bot_config = self.bot_service.get_bot(bot_id)

            if not bot_config or not bot_config.active:
                raise ValueError(f"Bot {bot_id} no está disponible")

            # 2. Buscar contexto relevante con threshold
            threshold = getattr(bot_config, 'retrieval_threshold', 0.3)
            retrieval_k = getattr(bot_config, 'retrieval_k', 5)
            max_sources = getattr(bot_config, 'max_sources', 5)

            context_chunks = self.retriever.search(
                query=user_question,
                bot_id=bot_id,
                k=retrieval_k,
                threshold=threshold
            )

            # Limitar número de fuentes
            context_chunks = context_chunks[:max_sources]

            # 3. Verificar strict_mode
            strict_mode = getattr(bot_config, 'strict_mode', True)

            if strict_mode and len(context_chunks) == 0:
                # No hay documentos relevantes y estamos en modo estricto
                fallback = getattr(
                    bot_config,
                    'fallback_response',
                    'Lo siento, no tengo información sobre eso en mi base de conocimiento.'
                )
                return {
                    "answer": fallback,
                    "sources": [],
                    "bot_config": {
                        "bot_id": bot_config.bot_id,
                        "name": bot_config.name,
                        "temperature": bot_config.temperature,
                        "strict_mode": strict_mode,
                        "threshold": threshold
                    },
                    "warning": "No se encontraron documentos relevantes (strict_mode activo)"
                }

            # 4. Construir contexto
            if len(context_chunks) > 0:
                context_text = "\n\n---\n\n".join([
                    f"[Fuente {i+1} - Similitud: {c['similarity']*100:.1f}%]\n{c['text']}"
                    for i, c in enumerate(context_chunks)
                ])
            else:
                context_text = "No se encontró información relevante en los documentos."

            # 5. Construir prompt según strict_mode
            if strict_mode:
                user_content = f"""Pregunta del usuario: {user_question}

Documentación disponible:
{context_text}

IMPORTANTE: Responde ÚNICAMENTE basándote en la documentación proporcionada arriba. Si la información no está en la documentación, indica que no tienes esa información."""
            else:
                user_content = f"""Pregunta del usuario: {user_question}

Documentación relevante:
{context_text}

Responde usando principalmente la documentación, pero puedes complementar con conocimiento general si es necesario."""

            messages = [
                {
                    "role": "system",
                    "content": bot_config.system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]

            # 6. Obtener respuesta del LLM
            answer = self.llm.chat(messages)

            return {
                "answer": answer,
                "sources": context_chunks,
                "bot_config": {
                    "bot_id": bot_config.bot_id,
                    "name": bot_config.name,
                    "temperature": bot_config.temperature,
                    "strict_mode": strict_mode,
                    "threshold": threshold,
                    "sources_found": len(context_chunks)
                }
            }

        except Exception as e:
            success = False
            error_msg = str(e)
            raise

        finally:
            # 7. Registrar métricas
            response_time_ms = (time.time() - start_time) * 1000

            self.analytics.log_interaction(
                bot_id=bot_id,
                question=user_question,
                answer=answer,
                sources_count=len(context_chunks),
                response_time_ms=response_time_ms,
                success=success,
                error=error_msg
            )

    def answer_stream(self, user_question: str, bot_id: str) -> Generator[str, None, None]:
        """
        Generador que yields chunks de respuesta en tiempo real con RAG preciso.

        Yields:
            Chunks en formato Server-Sent Events (SSE)
        """
        start_time = time.time()
        success = True
        error_msg = None
        full_answer = []
        context_chunks = []

        try:
            import json

            # 1. Obtener configuración del bot
            bot_config = self.bot_service.get_bot(bot_id)

            if not bot_config or not bot_config.active:
                raise ValueError(f"Bot {bot_id} no está disponible")

            # 2. Buscar contexto relevante con threshold
            threshold = getattr(bot_config, 'retrieval_threshold', 0.3)
            retrieval_k = getattr(bot_config, 'retrieval_k', 5)
            max_sources = getattr(bot_config, 'max_sources', 5)

            context_chunks = self.retriever.search(
                query=user_question,
                bot_id=bot_id,
                k=retrieval_k,
                threshold=threshold
            )

            # Limitar número de fuentes
            context_chunks = context_chunks[:max_sources]

            # 3. Enviar metadata inicial
            metadata = {
                "type": "metadata",
                "sources": context_chunks,
                "bot_config": {
                    "bot_id": bot_config.bot_id,
                    "name": bot_config.name,
                    "temperature": bot_config.temperature,
                    "strict_mode": getattr(bot_config, 'strict_mode', True),
                    "threshold": threshold,
                    "sources_found": len(context_chunks)
                }
            }
            yield f"data: {json.dumps(metadata)}\n\n"

            # 4. Verificar strict_mode
            strict_mode = getattr(bot_config, 'strict_mode', True)

            if strict_mode and len(context_chunks) == 0:
                # No hay documentos relevantes - enviar fallback
                fallback = getattr(
                    bot_config,
                    'fallback_response',
                    'Lo siento, no tengo información sobre eso en mi base de conocimiento.'
                )

                # Enviar fallback como chunk
                chunk_data = {
                    "type": "chunk",
                    "content": fallback
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"

                # Señal de finalización
                yield f"data: {json.dumps({'type': 'done', 'fallback': True})}\n\n"
                return

            # 5. Construir contexto
            if len(context_chunks) > 0:
                context_text = "\n\n---\n\n".join([
                    f"[Fuente {i+1} - Similitud: {c['similarity']*100:.1f}%]\n{c['text']}"
                    for i, c in enumerate(context_chunks)
                ])
            else:
                context_text = "No se encontró información relevante en los documentos."

            # 6. Construir prompt según strict_mode
            if strict_mode:
                user_content = f"""Pregunta del usuario: {user_question}

Documentación disponible:
{context_text}

IMPORTANTE: Responde ÚNICAMENTE basándote en la documentación proporcionada arriba. Si la información no está en la documentación, indica que no tienes esa información."""
            else:
                user_content = f"""Pregunta del usuario: {user_question}

Documentación relevante:
{context_text}

Responde usando principalmente la documentación, pero puedes complementar con conocimiento general si es necesario."""

            messages = [
                {
                    "role": "system",
                    "content": bot_config.system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]

            # 7. Stream de respuesta del LLM
            for chunk in self.llm.chat_stream(messages):
                full_answer.append(chunk)
                chunk_data = {
                    "type": "chunk",
                    "content": chunk
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"

            # 8. Enviar señal de finalización
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            success = False
            error_msg = str(e)
            error_data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"

        finally:
            # 9. Registrar métricas
            response_time_ms = (time.time() - start_time) * 1000
            answer = "".join(full_answer)

            self.analytics.log_interaction(
                bot_id=bot_id,
                question=user_question,
                answer=answer,
                sources_count=len(context_chunks),
                response_time_ms=response_time_ms,
                success=success,
                error=error_msg
            )


# Factory
def get_chat_service_enhanced():
    """Crea instancia del servicio de chat mejorado"""
    llm_client = get_llm_client()
    retriever = RetrieverService()
    bot_service = BotService()
    analytics_service = AnalyticsService()
    return ChatServiceEnhanced(llm_client, retriever, bot_service, analytics_service)
