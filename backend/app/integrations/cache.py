import json
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)

KEY_PREFIX = "docai"


class CacheService:
    def __init__(self):
        self._client = None
        self._connected = False
        self._ttl_config = {
            "document_summary": 86400,
            "faq_answer": 3600,
            "llm_response": 86400,
            "search_result": 3600,
            "chat_history": 1800,
            "user_preference": 604800,
            "rate_limit": 60,
            "session_data": 7200,
        }

    def _get_client(self):
        if self._client is None:
            try:
                import redis
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                    max_connections=100,
                )
                self._client.ping()
                self._connected = True
                logger.info(f"Redis连接成功: {settings.REDIS_URL}")
            except Exception as e:
                self._connected = False
                self._client = None
                logger.error(f"Redis连接失败: {e}")
                raise
        return self._client

    @property
    def client(self):
        return self._get_client()

    def is_connected(self) -> bool:
        if not self._connected or self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            self._connected = False
            return False

    def _reconnect(self):
        self.close()
        try:
            self._get_client()
            logger.info("Redis重连成功")
        except Exception as e:
            logger.error(f"Redis重连失败: {e}")
            raise

    def close(self):
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
            self._connected = False

    def _make_key(self, module: str, identifier: str, sub: str = "") -> str:
        parts = [KEY_PREFIX, "cache", module, identifier]
        if sub:
            parts.append(sub)
        return ":".join(parts)

    def _get_ttl(self, ttl_type: str, default_ttl: int = 3600) -> int:
        return self._ttl_config.get(ttl_type, default_ttl)

    def get(self, module: str, identifier: str, sub: str = "") -> Optional[str]:
        key = self._make_key(module, identifier, sub)
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"缓存命中: {key}")
            return value
        except Exception as e:
            logger.warning(f"缓存读取失败: {e}")
            self._connected = False
            try:
                self._reconnect()
                return self.client.get(key)
            except Exception:
                return None

    def set(
        self,
        module: str,
        identifier: str,
        value: str,
        ttl: int = None,
        sub: str = "",
    ) -> bool:
        key = self._make_key(module, identifier, sub)
        ttl = ttl or self._get_ttl(module)
        try:
            self.client.setex(key, ttl, value)
            logger.debug(f"缓存写入: {key}, TTL={ttl}s")
            return True
        except Exception as e:
            logger.warning(f"缓存写入失败: {e}")
            self._connected = False
            try:
                self._reconnect()
                self.client.setex(key, ttl, value)
                return True
            except Exception:
                return False

    def get_json(self, module: str, identifier: str, sub: str = "") -> Optional[Any]:
        value = self.get(module, identifier, sub)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    def set_json(
        self,
        module: str,
        identifier: str,
        value: Any,
        ttl: int = None,
        sub: str = "",
    ) -> bool:
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            return self.set(module, identifier, json_str, ttl, sub)
        except (TypeError, ValueError) as e:
            logger.warning(f"缓存序列化失败: {e}")
            return False

    def delete(self, module: str, identifier: str, sub: str = "") -> bool:
        key = self._make_key(module, identifier, sub)
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"缓存删除失败: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"模式删除失败: {e}")
            return 0

    def get_llm_cache(self, message_hash: str) -> Optional[str]:
        return self.get("llm", message_hash)

    def set_llm_cache(self, message_hash: str, response: str) -> bool:
        return self.set("llm", message_hash, response, ttl=self._get_ttl("llm_response"))

    def get_search_cache(self, query_hash: str) -> Optional[Any]:
        return self.get_json("search", query_hash)

    def set_search_cache(self, query_hash: str, results: Any) -> bool:
        return self.set_json("search", query_hash, results, ttl=self._get_ttl("search_result"))

    def set_rate_limit(self, user_id: str, endpoint: str, limit: int = 60) -> bool:
        key = f"{KEY_PREFIX}:rate_limit:{user_id}:{endpoint}"
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, self._get_ttl("rate_limit"))
            pipe.execute()
            return True
        except Exception as e:
            logger.warning(f"速率限制设置失败: {e}")
            return False

    def check_rate_limit(self, user_id: str, endpoint: str, limit: int = 60) -> bool:
        key = f"{KEY_PREFIX}:rate_limit:{user_id}:{endpoint}"
        try:
            count = self.client.get(key)
            if count and int(count) > limit:
                return False
            return True
        except Exception:
            return True

    def get_document_summary(self, document_id: str) -> Optional[Dict]:
        return self.get_json("document_summary", document_id)

    def set_document_summary(self, document_id: str, summary: Dict) -> bool:
        return self.set_json("document_summary", document_id, summary, ttl=self._get_ttl("document_summary"))

    def delete_document_summary(self, document_id: str) -> bool:
        return self.delete("document_summary", document_id)

    def get_faq_answer(self, question: str) -> Optional[str]:
        question_hash = hashlib.md5(question.encode()).hexdigest()
        return self.get("faq", question_hash)

    def set_faq_answer(self, question: str, answer: str) -> bool:
        question_hash = hashlib.md5(question.encode()).hexdigest()
        return self.set("faq", question_hash, answer, ttl=self._get_ttl("faq_answer"))

    def delete_faq_answer(self, question: str) -> bool:
        question_hash = hashlib.md5(question.encode()).hexdigest()
        return self.delete("faq", question_hash)

    def get_chat_history(self, user_id: str, chat_id: str) -> Optional[List]:
        return self.get_json("chat_history", user_id, sub=chat_id)

    def set_chat_history(self, user_id: str, chat_id: str, history: List) -> bool:
        return self.set_json("chat_history", user_id, history, ttl=self._get_ttl("chat_history"), sub=chat_id)

    def delete_chat_history(self, user_id: str, chat_id: str) -> bool:
        return self.delete("chat_history", user_id, sub=chat_id)

    def clear_user_chat_history(self, user_id: str) -> int:
        pattern = f"{KEY_PREFIX}:cache:chat_history:{user_id}:*"
        return self.delete_pattern(pattern)

    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        return self.get_json("user_preference", user_id)

    def set_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        return self.set_json("user_preference", user_id, preferences, ttl=self._get_ttl("user_preference"))

    def update_user_preferences(self, user_id: str, updates: Dict) -> bool:
        current = self.get_user_preferences(user_id) or {}
        current.update(updates)
        return self.set_user_preferences(user_id, current)

    def get_session_data(self, session_id: str) -> Optional[Dict]:
        return self.get_json("session", session_id)

    def set_session_data(self, session_id: str, data: Dict) -> bool:
        return self.set_json("session", session_id, data, ttl=self._get_ttl("session_data"))

    def delete_session_data(self, session_id: str) -> bool:
        return self.delete("session", session_id)

    def increment_counter(self, name: str, amount: int = 1) -> int:
        key = f"{KEY_PREFIX}:counter:{name}"
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.warning(f"计数器增量失败: {e}")
            return 0

    def get_counter(self, name: str) -> int:
        key = f"{KEY_PREFIX}:counter:{name}"
        try:
            value = self.client.get(key)
            return int(value) if value else 0
        except Exception:
            return 0

    def set_counter(self, name: str, value: int) -> bool:
        key = f"{KEY_PREFIX}:counter:{name}"
        try:
            self.client.set(key, value)
            return True
        except Exception as e:
            logger.warning(f"计数器设置失败: {e}")
            return False

    def cache_document_chunks(self, document_id: str, chunks: List[Dict]) -> bool:
        return self.set_json("document_chunks", document_id, chunks, ttl=86400)

    def get_document_chunks(self, document_id: str) -> Optional[List[Dict]]:
        return self.get_json("document_chunks", document_id)

    def cache_embedding(self, text: str, embedding: List[float]) -> bool:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.set_json("embedding", text_hash, embedding, ttl=3600)

    def get_embedding(self, text: str) -> Optional[List[float]]:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.get_json("embedding", text_hash)

    def warmup_cache(self):
        logger.info("开始预热缓存...")
        try:
            self.set("system", "warmup_time", datetime.now().isoformat(), ttl=3600)
            logger.info("缓存预热完成")
        except Exception as e:
            logger.error(f"缓存预热失败: {e}")

    def cleanup_expired(self):
        logger.info("清理过期缓存...")
        try:
            patterns = [
                f"{KEY_PREFIX}:cache:chat_history:*",
                f"{KEY_PREFIX}:cache:session:*",
            ]
            for pattern in patterns:
                deleted = self.delete_pattern(pattern)
                if deleted > 0:
                    logger.info(f"清理过期缓存: {pattern}, 删除 {deleted} 条")
            logger.info("过期缓存清理完成")
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")

    def get_stats(self) -> Dict[str, Any]:
        try:
            info = self.client.info("stats")
            return {
                "keys": info.get("keys", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "hit_rate": info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1), 1) * 100,
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            logger.warning(f"获取缓存统计失败: {e}")
            return {}

    def ping(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            self._connected = False
            return False


cache_service = CacheService()
