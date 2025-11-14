from app.services.vector_service import VectorService

class RetrieverService:
    """
    Servicio que consulta en Chroma los chunks más parecidos.
    Filtra resultados por bot_id para multi-tenancy.
    """
    def __init__(self):
        self.vector_service = VectorService()

    def search(self, query: str, bot_id: str, k: int = 5):
        # Ahora sí filtramos por bot_id para aislar cada chatbot
        # k es configurable por bot (retrieval_k en bots_config.json)
        results = self.vector_service.query(query_text=query, n_results=k, bot_id=bot_id)

        # Chroma devuelve varias listas paralelas, las unimos
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]  # si está disponible

        combined = []
        for i, doc in enumerate(documents):
            combined.append({
                "text": doc,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "score": distances[i] if i < len(distances) else None,
            })

        return combined
