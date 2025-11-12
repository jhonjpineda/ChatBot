import chromadb
from chromadb.config import Settings
from app.services.embedding_service import EmbeddingService

class VectorService:
    """
    Encapsula ChromaDB.
    Usamos una sola colección por ahora (luego podemos separar por bot_id).
    """
    def __init__(self, collection_name: str = "chatbot_docs"):
        self.embedding_service = EmbeddingService()
        self.client = chromadb.PersistentClient(
            path="chroma_db",  # carpeta donde guarda la data
            settings=Settings()
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_document_chunks(self, doc_id: str, chunks: list[str], metadata: dict | None = None):
        # generamos ids únicos por chunk
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        embeddings = self.embedding_service.embed(chunks)

        metadatas = []
        for i, c in enumerate(chunks):
            md = {"doc_id": doc_id}
            if metadata:
                md.update(metadata)
            metadatas.append(md)

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query(self, query_text: str, n_results: int = 4):
        query_embedding = self.embedding_service.embed([query_text])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
