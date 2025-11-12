from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    # validamos tipo
    if file.content_type not in ["application/pdf"]:
        raise HTTPException(status_code=400, detail="Solo se aceptan PDFs por ahora.")

    service = DocumentService()
    doc_info = await service.process_upload(file)

    return {
        "message": "Documento cargado e indexado correctamente",
        "document": doc_info
    }
