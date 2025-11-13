from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.document_service import DocumentService

router = APIRouter()

ALLOWED_CONTENT_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "text/plain"  # .txt
]

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(..., description="Archivo a subir (max 50MB)"),
    bot_id: str = Query(default="default", description="ID del bot al que pertenece el documento")
):
    """
    Sube y procesa un documento (PDF, DOCX, TXT) para un bot específico.
    El documento será indexado y disponible solo para ese bot.
    Tamaño máximo: 50MB
    """
    # Validar tamaño del archivo (50MB = 50 * 1024 * 1024 bytes)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    # Leer contenido para verificar tamaño
    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo es demasiado grande. Tamaño máximo: 50MB. Tu archivo: {file_size / (1024*1024):.2f}MB"
        )

    # Restaurar el puntero del archivo al inicio
    await file.seek(0)

    # Validar tipo
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado. Acepta: PDF, DOCX, TXT. Recibido: {file.content_type}"
        )

    try:
        service = DocumentService()
        doc_info = await service.process_upload(file, bot_id=bot_id)

        return {
            "message": "Documento cargado e indexado correctamente",
            "document": doc_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el documento: {str(e)}"
        )

@router.get("/list")
async def list_documents(
    bot_id: str | None = Query(default=None, description="Filtrar documentos por bot_id")
):
    """
    Lista todos los documentos indexados.
    Si se proporciona bot_id, filtra solo los documentos de ese bot.
    """
    service = DocumentService()
    documents = service.list_documents(bot_id=bot_id)

    return {
        "documents": documents,
        "total": len(documents)
    }

@router.patch("/{doc_id}/move")
async def move_document_to_bot(
    doc_id: str,
    new_bot_id: str = Query(..., description="Nuevo bot_id al que mover el documento")
):
    """
    Cambia el bot_id de un documento existente.
    Útil cuando se sube un documento al bot equivocado.
    """
    service = DocumentService()

    try:
        service.move_document_to_bot(doc_id, new_bot_id)
        return {
            "message": f"Documento movido al bot '{new_bot_id}' correctamente",
            "doc_id": doc_id,
            "new_bot_id": new_bot_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al mover documento: {str(e)}")

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """
    Elimina un documento específico de la base vectorial.
    """
    service = DocumentService()

    try:
        service.delete_document(doc_id)
        return {
            "message": "Documento eliminado correctamente",
            "doc_id": doc_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar documento: {str(e)}")
