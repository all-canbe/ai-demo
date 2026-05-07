from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, FAQ
from app.redis_cache import redis_cache

router = APIRouter()

@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return [{"id": doc.id, "filename": doc.filename, "status": doc.status} for doc in documents]

@router.get("/documents/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    redis_cache.delete_document_summary(document_id)
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}

@router.get("/faqs")
def list_faqs(db: Session = Depends(get_db)):
    faqs = db.query(FAQ).all()
    return [{"id": faq.id, "question": faq.question} for faq in faqs]

@router.get("/faqs/{faq_id}")
def get_faq(faq_id: int, db: Session = Depends(get_db)):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq

@router.delete("/faqs/{faq_id}")
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    redis_cache.delete_faq_answer(faq.question)
    db.delete(faq)
    db.commit()
    
    return {"message": "FAQ deleted successfully"}

@router.post("/cache/flush")
def flush_cache():
    redis_cache.flush_all()
    return {"message": "Cache flushed successfully"}

@router.get("/cache/status")
def cache_status():
    return {"status": "operational"}
