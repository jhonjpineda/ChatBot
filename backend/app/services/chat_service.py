import time
from app.services.retriever_service import RetrieverService
from app.services.bot_service import BotService
from app.services.analytics_service import AnalyticsService
from app.llm_providers.factory import get_llm_client

class ChatService:
    def __init__(self, llm_client, retriever: RetrieverService, bot_service: BotService, analytics_service: AnalyticsService):
        self.llm = llm_client
        self.retriever = retriever
        self.bot_service = bot_service
        self.analytics = analytics_service

    def answer(self, user_question: str, bot_id: str):
        start_time = time.time()
        success = True
        error_msg = None
        answer = ""
        context_chunks = []

        try:
            # 1. Obtener configuración del bot
            bot_config = self.bot_service.get_bot(bot_id)

            if not bot_config:
                # Usar configuración por defecto si no existe el bot
                print(f"⚠️ Bot {bot_id} no encontrado, usando configuración por defecto")
                bot_config = self.bot_service.get_bot("default")

            if not bot_config or not bot_config.active:
                raise ValueError(f"Bot {bot_id} no está disponible")

            # 2. Buscar contexto relevante
            context_chunks = self.retriever.search(user_question, bot_id)
            context_text = "\n".join(c["text"] for c in context_chunks)

            # 3. Construir mensajes usando el prompt del bot
            messages = [
                {
                    "role": "system",
                    "content": bot_config.system_prompt
                },
                {
                    "role": "user",
                    "content": f"Pregunta: {user_question}\n\nContexto:\n{context_text}"
                }
            ]

            # 4. Obtener respuesta del LLM
            answer = self.llm.chat(messages)

            return {
                "answer": answer,
                "sources": context_chunks,
                "bot_config": {
                    "bot_id": bot_config.bot_id,
                    "name": bot_config.name,
                    "temperature": bot_config.temperature
                }
            }

        except Exception as e:
            success = False
            error_msg = str(e)
            raise

        finally:
            # 5. Registrar métricas
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

    def answer_stream(self, user_question: str, bot_id: str):
        """
        Generador que yields chunks de respuesta en tiempo real.
        Primero yields las fuentes, luego los chunks de texto del LLM.
        """
        start_time = time.time()
        success = True
        error_msg = None
        full_answer = []

        try:
            # 1. Obtener configuración del bot
            bot_config = self.bot_service.get_bot(bot_id)

            if not bot_config:
                print(f"⚠️ Bot {bot_id} no encontrado, usando configuración por defecto")
                bot_config = self.bot_service.get_bot("default")

            if not bot_config or not bot_config.active:
                raise ValueError(f"Bot {bot_id} no está disponible")

            # 2. Buscar contexto relevante
            context_chunks = self.retriever.search(user_question, bot_id)
            context_text = "\n".join(c["text"] for c in context_chunks)

            # 3. Enviar metadata inicial (fuentes y configuración del bot)
            import json
            metadata = {
                "type": "metadata",
                "sources": context_chunks,
                "bot_config": {
                    "bot_id": bot_config.bot_id,
                    "name": bot_config.name,
                    "temperature": bot_config.temperature
                }
            }
            yield f"data: {json.dumps(metadata)}\n\n"

            # 4. Construir mensajes
            messages = [
                {
                    "role": "system",
                    "content": bot_config.system_prompt
                },
                {
                    "role": "user",
                    "content": f"Pregunta: {user_question}\n\nContexto:\n{context_text}"
                }
            ]

            # 5. Stream de respuesta del LLM
            for chunk in self.llm.chat_stream(messages):
                full_answer.append(chunk)
                chunk_data = {
                    "type": "chunk",
                    "content": chunk
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"

            # 6. Enviar señal de finalización
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
            # 7. Registrar métricas
            response_time_ms = (time.time() - start_time) * 1000
            answer = "".join(full_answer)

            self.analytics.log_interaction(
                bot_id=bot_id,
                question=user_question,
                answer=answer,
                sources_count=len(context_chunks) if 'context_chunks' in locals() else 0,
                response_time_ms=response_time_ms,
                success=success,
                error=error_msg
            )

# factory
def get_chat_service():
    llm_client = get_llm_client()
    retriever = RetrieverService()
    bot_service = BotService()
    analytics_service = AnalyticsService()
    return ChatService(llm_client, retriever, bot_service, analytics_service)
