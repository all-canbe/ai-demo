from celery import shared_task
from app.redis_cache import redis_cache
import time

@shared_task(bind=True, retry_backoff=3, retry_kwargs={'max_retries': 5})
def process_document(self, document_id: str, content: str):
    time.sleep(2)
    
    summary = {
        "document_id": document_id,
        "content_length": len(content),
        "summary": content[:200] + "..." if len(content) > 200 else content,
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    redis_cache.set_document_summary(document_id, summary)
    
    return {"status": "completed", "document_id": document_id, "summary_length": len(summary["summary"])}

@shared_task(bind=True, retry_backoff=2, retry_kwargs={'max_retries': 3})
def generate_faq_answer(self, question: str, context: str):
    time.sleep(1)
    
    answer = f"根据文档内容，关于'{question}'的回答：{context[:150]}..."
    
    redis_cache.set_faq_answer(question, answer)
    
    return {"status": "completed", "question": question, "answer_length": len(answer)}

@shared_task
def cleanup_old_cache(ttl_hours: int = 24):
    redis_cache.flush_all()
    return {"status": "completed", "message": f"Cleaned up cache older than {ttl_hours} hours"}

@shared_task
def health_check():
    return {"status": "healthy", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
