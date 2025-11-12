from app.services.vector_service import VectorService

class RetrieverService:
    """
    Servicio que consulta en Chroma los chunks más parecidos.
    Por ahora no filtramos por bot_id, pero el campo ya está en los metadatos.
    """
    def __init__(self):
        self.vector_service = VectorService()

    def search(self, query: str, bot_id: str):
        results = self.vector_service.query(query_text=query, n_results=4)

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
