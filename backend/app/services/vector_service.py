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

    def query(self, query_text: str, n_results: int = 4, bot_id: str | None = None):
        """
        Busca chunks similares en la colección.
        Si se proporciona bot_id, filtra solo los documentos de ese bot.
        """
        query_embedding = self.embedding_service.embed([query_text])[0]

        # Preparar filtro si bot_id está presente
        where_filter = {"bot_id": bot_id} if bot_id else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        return results

    def update_document_bot_id(self, doc_id: str, new_bot_id: str):
        """
        Actualiza el bot_id de todos los chunks de un documento.
        Usado para mover documentos entre bots.
        """
        # Obtener todos los chunks del documento
        results = self.collection.get(where={"doc_id": doc_id})

        if not results['ids']:
            raise ValueError(f"Documento {doc_id} no encontrado")

        # Actualizar metadata de cada chunk
        ids = results['ids']
        metadatas = results['metadatas']

        # Actualizar bot_id en cada metadata
        updated_metadatas = []
        for metadata in metadatas:
            updated_metadata = metadata.copy()
            updated_metadata['bot_id'] = new_bot_id
            updated_metadatas.append(updated_metadata)

        # Actualizar en ChromaDB
        self.collection.update(
            ids=ids,
            metadatas=updated_metadatas
        )

    def delete_by_doc_id(self, doc_id: str):
        """Elimina todos los chunks de un documento específico."""
        self.collection.delete(where={"doc_id": doc_id})

    def delete_by_bot_id(self, bot_id: str):
        """Elimina todos los documentos de un bot específico."""
        self.collection.delete(where={"bot_id": bot_id})

    def list_documents(self, bot_id: str | None = None):
        """Lista todos los documentos, opcionalmente filtrados por bot_id."""
        where_filter = {"bot_id": bot_id} if bot_id else None
        results = self.collection.get(where=where_filter)

        # Agrupar por doc_id para obtener lista única de documentos
        doc_ids = set()
        documents = []

        if results and results.get('metadatas'):
            for metadata in results['metadatas']:
                doc_id = metadata.get('doc_id')
                if doc_id and doc_id not in doc_ids:
                    doc_ids.add(doc_id)
                    documents.append({
                        'doc_id': doc_id,
                        'bot_id': metadata.get('bot_id'),
                        'filename': metadata.get('filename'),
                        'uploaded_at': metadata.get('uploaded_at')
                    })

        return documents
