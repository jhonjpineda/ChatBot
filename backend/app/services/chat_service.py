from app.services.retriever_service import RetrieverService
from app.llm_providers.factory import get_llm_client

class ChatService:
    def __init__(self, llm_client, retriever: RetrieverService):
        self.llm = llm_client
        self.retriever = retriever

    def answer(self, user_question: str, bot_id: str):
        # 1. buscar contexto (por ahora vacío, luego lo conectamos a Chroma)
        context_chunks = self.retriever.search(user_question, bot_id)
        context_text = "\n".join(c["text"] for c in context_chunks)

        messages = [
            {
                "role": "system",
                "content": "Eres un chatbot que responde SOLO con la información del contexto. Si no está, di que no está."
            },
            {
                "role": "user",
                "content": f"Pregunta: {user_question}\n\nContexto:\n{context_text}"
            }
        ]

        answer = self.llm.chat(messages)

        return {
            "answer": answer,
            "sources": context_chunks
        }

# factory
def get_chat_service():
    llm_client = get_llm_client()
    retriever = RetrieverService()
    return ChatService(llm_client, retriever)
