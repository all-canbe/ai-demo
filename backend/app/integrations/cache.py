import json
from typing import Any, Optional
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)

KEY_PREFIX = "docai"


class CacheService:
    def __init__(self):
        self._client = None
        self._connected = False

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
        ttl: int = 3600,
        sub: str = "",
    ) -> bool:
        key = self._make_key(module, identifier, sub)
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
        ttl: int = 3600,
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

    def get_llm_cache(self, message_hash: str) -> Optional[str]:
        return self.get("llm", message_hash)

    def set_llm_cache(self, message_hash: str, response: str) -> bool:
        return self.set("llm", message_hash, response, ttl=86400)

    def get_search_cache(self, query_hash: str) -> Optional[Any]:
        return self.get_json("search", query_hash)

    def set_search_cache(self, query_hash: str, results: Any) -> bool:
        return self.set_json("search", query_hash, results, ttl=3600)

    def set_rate_limit(self, user_id: str, endpoint: str, limit: int = 60) -> bool:
        key = f"{KEY_PREFIX}:rate_limit:{user_id}:{endpoint}"
        try:
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
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

    def ping(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            self._connected = False
            return False


cache_service = CacheService()
