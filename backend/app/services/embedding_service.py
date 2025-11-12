from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """
    Wrap del modelo de embeddings.
    Lo separamos para que luego podamos cambiar a OpenAI.
    """
    def __init__(self):
        # modelo liviano y bueno
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()
