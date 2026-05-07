from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import uuid4
from app.config import settings
from app.database import get_db, engine
from app.models import Base
from app.redis_cache import redis_cache
from app.tasks import process_document, generate_faq_answer, health_check
from app import routes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Document Analyzer API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}

@app.get("/health")
async def health():
    result = health_check.delay()
    return {"status": "healthy", "service": "fastapi"}

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    document_id = str(uuid4())
    
    content = await file.read()
    content_str = content.decode("utf-8")
    
    process_document.delay(document_id, content_str)
    
    return {"document_id": document_id, "filename": file.filename, "status": "processing"}

@app.get("/documents/{document_id}/summary")
async def get_document_summary(document_id: str):
    summary = redis_cache.get_document_summary(document_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found or not yet processed")
    return summary

@app.post("/faq/query")
async def query_faq(question: str, document_id: str = None):
    cached_answer = redis_cache.get_faq_answer(question)
    if cached_answer:
        return {"question": question, "answer": cached_answer, "source": "cache"}
    
    context = f"Document content for {document_id}" if document_id else "General knowledge"
    generate_faq_answer.delay(question, context)
    
    return {"question": question, "answer": "Processing your question...", "source": "processing"}

app.include_router(routes.router, prefix=settings.API_PREFIX)
