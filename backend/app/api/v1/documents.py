import math
import os
from fastapi import APIRouter, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, List
from app.api.deps import DBSession, CurrentUser
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.document import DocumentUploadResponse, DocumentItem, DocumentStatusResponse, DocumentSummaryResponse
from app.services import document_service, summary_service
from app.config.settings import settings
from app.processing.llm.summarizer import DocumentSummarizer
from app.processing.document.parser import DocumentParser

router = APIRouter(prefix="/documents", tags=["documents"])

summarizer = DocumentSummarizer(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)
parser = DocumentParser(settings.TESSERACT_PATH)


@router.post("")
async def upload_document(
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None),
):
    file_content = await file.read()
    document = await document_service.upload_document(
        db=db,
        user=current_user,
        file_content=file_content,
        filename=file.filename or "unknown",
        folder_id=folder_id,
    )
    return ApiResponse(
        data=DocumentUploadResponse(
            id=document.id,
            name=document.name,
            type=document.type,
            size=document.size,
            upload_time=document.created_at,
            processing_status=document.processing_status.value,
        )
    )


@router.get("")
async def get_documents(
    db: DBSession,
    current_user: CurrentUser,
    folder_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
):
    documents, total = await document_service.get_document_list(
        db=db,
        user=current_user,
        folder_id=folder_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    items = [
        DocumentItem(
            id=doc.id,
            name=doc.name,
            type=doc.type,
            size=doc.size,
            upload_time=doc.created_at,
            processing_status=doc.processing_status.value,
            folder_id=doc.folder_id,
        )
        for doc in documents
    ]
    return ApiResponse(
        data=PaginatedData(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )
    )


@router.get("/{doc_id}")
async def get_document_detail(
    db: DBSession,
    current_user: CurrentUser,
    doc_id: str,
):
    document = await document_service.get_document_detail(db, doc_id, current_user)
    return ApiResponse(
        data=DocumentItem(
            id=document.id,
            name=document.name,
            type=document.type,
            size=document.size,
            upload_time=document.created_at,
            processing_status=document.processing_status.value,
            folder_id=document.folder_id,
        )
    )


@router.delete("/{doc_id}")
async def delete_document(
    db: DBSession,
    current_user: CurrentUser,
    doc_id: str,
):
    await document_service.delete_document(db, doc_id, current_user)
    return ApiResponse(message="文档删除成功")


@router.get("/{doc_id}/status")
async def get_document_status(
    db: DBSession,
    current_user: CurrentUser,
    doc_id: str,
):
    status_data = await document_service.get_document_status(db, doc_id, current_user)
    return ApiResponse(data=DocumentStatusResponse(**status_data))


@router.get("/{doc_id}/summary")
async def get_document_summary(
    db: DBSession,
    current_user: CurrentUser,
    doc_id: str,
):
    summary_data = await summary_service.get_document_summary(db, doc_id, current_user.id)
    return ApiResponse(data=DocumentSummaryResponse(**summary_data))


@router.post("/{doc_id}/retry")
async def retry_document(
    db: DBSession,
    current_user: CurrentUser,
    doc_id: str,
):
    document = await document_service.retry_document(db, doc_id, current_user)
    return ApiResponse(
        data=DocumentUploadResponse(
            id=document.id,
            name=document.name,
            type=document.type,
            size=document.size,
            upload_time=document.created_at,
            processing_status=document.processing_status.value,
        )
    )


@router.get("/{doc_id}/download")
async def download_document(
    db: DBSession,
    current_user: CurrentUser,
    doc_id: str,
):
    document = await document_service.get_document_detail(db, doc_id, current_user)
    
    if not os.path.exists(document.file_path):
        from app.utils.exceptions import NotFoundException
        from app.schemas.common import ErrorCode
        raise NotFoundException(
            error_code=ErrorCode.DOC_NOT_FOUND,
            message="文件不存在",
        )
    
    return FileResponse(
        path=document.file_path,
        filename=document.name,
        media_type="application/octet-stream",
    )


@router.post("/{doc_id}/summarize/stream")
async def summarize_document_stream(
    db: DBSession,
    current_user: CurrentUser,
    doc_id: str,
):
    document = await document_service.get_document_detail(db, doc_id, current_user)
    
    if not os.path.exists(document.file_path):
        from app.utils.exceptions import NotFoundException
        from app.schemas.common import ErrorCode
        raise NotFoundException(
            error_code=ErrorCode.DOC_NOT_FOUND,
            message="文件不存在",
        )
    
    with open(document.file_path, "rb") as f:
        file_content = f.read()
    
    parsed = parser.parse(document.name, file_content)
    
    def _extract_text(parsed):
        if isinstance(parsed, list):
            if all(isinstance(item, dict) and "text" in item for item in parsed):
                return "\n\n".join(item["text"] for item in parsed)
        elif isinstance(parsed, dict):
            if "text" in parsed:
                return parsed["text"]
            elif "paragraphs" in parsed:
                return "\n\n".join(p["text"] for p in parsed["paragraphs"])
        return str(parsed)
    
    text = _extract_text(parsed)
    
    async def generate():
        for chunk in summarizer.summarize_stream(text):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/plain")


@router.post("/{doc_id}/key-points")
async def extract_key_points(
    db: DBSession,
    current_user: CurrentUser,
    doc_id: str,
    max_points: int = Query(5, ge=1, le=10),
):
    document = await document_service.get_document_detail(db, doc_id, current_user)
    
    if not os.path.exists(document.file_path):
        from app.utils.exceptions import NotFoundException
        from app.schemas.common import ErrorCode
        raise NotFoundException(
            error_code=ErrorCode.DOC_NOT_FOUND,
            message="文件不存在",
        )
    
    with open(document.file_path, "rb") as f:
        file_content = f.read()
    
    parsed = parser.parse(document.name, file_content)
    
    def _extract_text(parsed):
        if isinstance(parsed, list):
            if all(isinstance(item, dict) and "text" in item for item in parsed):
                return "\n\n".join(item["text"] for item in parsed)
        elif isinstance(parsed, dict):
            if "text" in parsed:
                return parsed["text"]
            elif "paragraphs" in parsed:
                return "\n\n".join(p["text"] for p in parsed["paragraphs"])
        return str(parsed)
    
    text = _extract_text(parsed)
    key_points = summarizer.extract_key_points(text, max_points)
    
    return ApiResponse(data={"document_id": doc_id, "key_points": key_points})


@router.post("/batch-process")
async def batch_process_documents(
    db: DBSession,
    current_user: CurrentUser,
    files: List[UploadFile] = File(...),
):
    results = []
    for file in files:
        try:
            file_content = await file.read()
            document = await document_service.upload_document(
                db=db,
                user=current_user,
                file_content=file_content,
                filename=file.filename or "unknown",
                folder_id=None,
            )
            results.append({
                "filename": file.filename,
                "success": True,
                "document_id": document.id,
                "processing_status": document.processing_status.value,
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e),
            })
    
    return ApiResponse(data={"results": results})
