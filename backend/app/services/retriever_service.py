from app.services.vector_service import VectorService
from typing import List, Dict, Any, Optional

class RetrieverService:
    """
    Servicio que consulta en Chroma los chunks más parecidos.
    Filtra resultados por bot_id para multi-tenancy y por threshold de similitud.
    """
    def __init__(self):
        self.vector_service = VectorService()

    @staticmethod
    def distance_to_similarity(distance: float) -> float:
        """
        Convierte distancia de ChromaDB a score de similitud (0.0-1.0).

        ChromaDB usa distancia L2 (Euclidean):
        - distance = 0.0 → 100% similar (similarity = 1.0)
        - distance = 1.0 → ~50% similar (similarity = 0.5)
        - distance = 2.0 → 0% similar (similarity = 0.0)

        Formula: similarity = max(0, 1 - distance)
        """
        return max(0.0, min(1.0, 1.0 - distance))

    def search(
        self,
        query: str,
        bot_id: str,
        k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca chunks relevantes en el vector store.

        Args:
            query: Pregunta del usuario
            bot_id: ID del bot (para multi-tenancy)
            k: Número de resultados a recuperar
            threshold: Umbral mínimo de similitud (0.0-1.0). Chunks con score menor serán descartados.

        Returns:
            Lista de chunks con texto, metadata y similarity score
        """
        # Buscar en ChromaDB
        results = self.vector_service.query(query_text=query, n_results=k, bot_id=bot_id)

        # Chroma devuelve listas paralelas, las unimos
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        combined = []
        for i, doc in enumerate(documents):
            # Convertir distancia a similarity score
            distance = distances[i] if i < len(distances) else 1.0
            similarity = self.distance_to_similarity(distance)

            # Filtrar por threshold si está definido
            if threshold is not None and similarity < threshold:
                continue

            combined.append({
                "text": doc,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "distance": distance,
                "similarity": round(similarity, 3),  # Score normalizado 0-1
            })

        return combined
