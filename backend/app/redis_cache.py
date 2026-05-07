import json
from typing import Any, Optional
import redis
from app.config import settings

class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.default_ttl = settings.REDIS_CACHE_TTL

    def get_document_summary(self, document_id: str) -> Optional[dict]:
        key = f"doc:summary:{document_id}"
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set_document_summary(self, document_id: str, summary: dict, ttl: Optional[int] = None) -> None:
        key = f"doc:summary:{document_id}"
        self.client.setex(key, ttl or self.default_ttl, json.dumps(summary))

    def delete_document_summary(self, document_id: str) -> None:
        key = f"doc:summary:{document_id}"
        self.client.delete(key)

    def get_faq_answer(self, question: str) -> Optional[str]:
        key = f"faq:answer:{question}"
        return self.client.get(key)

    def set_faq_answer(self, question: str, answer: str, ttl: Optional[int] = None) -> None:
        key = f"faq:answer:{question}"
        self.client.setex(key, ttl or self.default_ttl, answer)

    def delete_faq_answer(self, question: str) -> None:
        key = f"faq:answer:{question}"
        self.client.delete(key)

    def get(self, key: str) -> Optional[str]:
        return self.client.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.client.setex(key, ttl or self.default_ttl, value)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0

    def flush_all(self) -> None:
        self.client.flushdb()

redis_cache = RedisCache()
