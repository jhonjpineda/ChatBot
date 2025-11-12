import os
import uuid
from typing import List

from fastapi import UploadFile
from pypdf import PdfReader

from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

UPLOAD_DIR = "uploads"


class DocumentService:
    """
    Servicio para:
    1. guardar el archivo
    2. extraer texto
    3. trocear
    4. vectorizar
    5. guardar en Chroma
    """

    def __init__(self):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()

    async def process_upload(self, file: UploadFile):
        # 1. guardar archivo físico
        saved_path = await self._save_file(file)

        # 2. extraer texto
        text = self._extract_text_from_pdf(saved_path)

        # 3. trocear
        chunks = self._chunk_text(text, chunk_size=800)

        # 4. generar embeddings y guardar en vector db
        doc_id = str(uuid.uuid4())
        self.vector_service.add_document_chunks(
            doc_id=doc_id,
            chunks=chunks,
            metadata={"filename": file.filename}
        )

        return {
            "id": doc_id,
            "filename": file.filename,
            "path": saved_path,
            "chunks": len(chunks)
        }

    async def _save_file(self, file: UploadFile) -> str:
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)

        return filepath

    def _extract_text_from_pdf(self, path: str) -> str:
        reader = PdfReader(path)
        all_text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            all_text.append(page_text)
        return "\n".join(all_text)

    def _chunk_text(self, text: str, chunk_size: int = 800) -> List[str]:
        words = text.split()
        chunks = []
        current = []
        current_len = 0

        for w in words:
            current.append(w)
            current_len += len(w) + 1
            if current_len >= chunk_size:
                chunks.append(" ".join(current))
                current = []
                current_len = 0

        if current:
            chunks.append(" ".join(current))

        return chunks
