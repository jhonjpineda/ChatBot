import os
import uuid
from typing import List
from datetime import datetime

from fastapi import UploadFile
from pypdf import PdfReader
from docx import Document

from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.analytics_service import AnalyticsService

UPLOAD_DIR = "uploads"


class DocumentService:
    """
    Servicio para:
    1. guardar el archivo
    2. extraer texto (PDF, DOCX, TXT)
    3. trocear con overlap inteligente
    4. vectorizar
    5. guardar en Chroma con aislamiento por bot_id
    """

    def __init__(self):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.analytics = AnalyticsService()

    async def process_upload(self, file: UploadFile, bot_id: str = "default"):
        # 1. guardar archivo físico
        saved_path = await self._save_file(file)

        # 2. extraer texto según el tipo de archivo
        if file.content_type == "application/pdf":
            text = self._extract_text_from_pdf(saved_path)
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = self._extract_text_from_docx(saved_path)
        elif file.content_type == "text/plain":
            text = self._extract_text_from_txt(saved_path)
        else:
            text = self._extract_text_from_pdf(saved_path)  # fallback

        # 3. trocear en chunks con overlap
        chunks = self._chunk_text(text, chunk_size=800, overlap=100)

        # 4. generar embeddings y guardar en vector db
        doc_id = str(uuid.uuid4())

        self.vector_service.add_document_chunks(
            doc_id=doc_id,
            chunks=chunks,
            metadata={
                "filename": file.filename,
                "bot_id": bot_id,
                "uploaded_at": datetime.now().isoformat(),
                "file_type": file.content_type
            }
        )

        print(f"✅ Documento indexado: {file.filename} ({len(chunks)} fragmentos)")

        # Registrar en analytics
        self.analytics.log_document_upload(
            bot_id=bot_id,
            filename=file.filename,
            chunks_count=len(chunks)
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
        """Extrae texto completo de un PDF"""
        reader = PdfReader(path)
        all_text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            all_text.append(page_text)
        return "\n".join(all_text)

    def _extract_text_from_docx(self, path: str) -> str:
        """Extrae texto completo de un DOCX"""
        doc = Document(path)
        all_text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                all_text.append(paragraph.text)
        return "\n".join(all_text)

    def _extract_text_from_txt(self, path: str) -> str:
        """Extrae texto completo de un TXT"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
        """
        Divide el texto en fragmentos manejables con overlap.
        Intenta respetar límites de párrafos cuando es posible.
        """
        # Primero dividir por párrafos
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

        chunks = []
        current_chunk = []
        current_length = 0

        for paragraph in paragraphs:
            paragraph_length = len(paragraph)

            # Si el párrafo solo cabe en un nuevo chunk
            if current_length + paragraph_length > chunk_size and current_chunk:
                # Guardar chunk actual
                chunks.append(" ".join(current_chunk))

                # Iniciar nuevo chunk con overlap del anterior
                overlap_text = " ".join(current_chunk)
                if len(overlap_text) > overlap:
                    # Tomar las últimas palabras del chunk anterior
                    overlap_words = overlap_text.split()
                    overlap_start = max(0, len(overlap_words) - (overlap // 10))
                    current_chunk = overlap_words[overlap_start:]
                    current_length = len(" ".join(current_chunk))
                else:
                    current_chunk = []
                    current_length = 0

            # Agregar párrafo al chunk actual
            current_chunk.append(paragraph)
            current_length += paragraph_length

        # Agregar último chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def move_document_to_bot(self, doc_id: str, new_bot_id: str):
        """
        Mueve un documento de un bot a otro.
        Actualiza el metadata bot_id de todos los chunks del documento.
        """
        self.vector_service.update_document_bot_id(doc_id, new_bot_id)
        print(f"📦 Documento {doc_id} movido al bot {new_bot_id}")

    def delete_document(self, doc_id: str):
        """Elimina un documento específico de la base vectorial"""
        self.vector_service.delete_by_doc_id(doc_id)
        print(f"🗑️ Documento {doc_id} eliminado")

    def list_documents(self, bot_id: str | None = None):
        """Lista todos los documentos, opcionalmente filtrados por bot_id"""
        return self.vector_service.list_documents(bot_id=bot_id)
