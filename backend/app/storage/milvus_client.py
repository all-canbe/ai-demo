from typing import Any, Optional
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "document_chunks"


class MilvusClient:
    def __init__(self):
        self._client = None
        self._connected = False

    def _get_client(self):
        if self._client is None:
            try:
                from pymilvus import MilvusClient as _MilvusClient
                self._client = _MilvusClient(
                    uri=f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}",
                    timeout=10,
                )
                self._client.list_collections()
                self._connected = True
                logger.info(f"Milvus连接成功: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
            except Exception as e:
                self._connected = False
                self._client = None
                logger.error(f"Milvus连接失败: {e}")
                raise
        return self._client

    @property
    def client(self):
        return self._get_client()

    def is_connected(self) -> bool:
        if not self._connected or self._client is None:
            return False
        try:
            self._client.list_collections()
            return True
        except Exception:
            self._connected = False
            return False

    def _reconnect(self):
        self.close()
        try:
            self._get_client()
            logger.info("Milvus重连成功")
        except Exception as e:
            logger.error(f"Milvus重连失败: {e}")
            raise

    def list_collections(self):
        try:
            return self.client.list_collections()
        except Exception as e:
            logger.error(f"Milvus list_collections失败: {e}")
            self._reconnect()
            return self.client.list_collections()

    def ensure_collection(self) -> None:
        collections = self.list_collections()
        if COLLECTION_NAME in collections:
            return

        from pymilvus import CollectionSchema, FieldSchema, DataType

        schema = CollectionSchema(
            fields=[
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=36, is_primary=True),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.OPENAI_EMBEDDING_DIMENSION),
                FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=36),
                FieldSchema(name="section_id", dtype=DataType.VARCHAR, max_length=50),
                FieldSchema(name="page", dtype=DataType.INT64),
                FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=20),
            ],
            description="文档片段向量集合",
        )

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            schema=schema,
        )

        self.client.create_index(
            collection_name=COLLECTION_NAME,
            field_name="embedding",
            index_params={
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 1024},
            },
        )

        self.client.create_index(
            collection_name=COLLECTION_NAME,
            field_name="document_id",
            index_params={"index_type": "STL_SORT"},
        )

        logger.info(f"Milvus集合 {COLLECTION_NAME} 创建成功")

    def insert_chunks(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> int:
        self.ensure_collection()

        data = []
        for chunk, embedding in zip(chunks, embeddings):
            data.append({
                "id": chunk["id"],
                "content": chunk["content"],
                "embedding": embedding,
                "document_id": chunk["document_id"],
                "section_id": chunk.get("section_id", ""),
                "page": chunk.get("page", 0),
                "type": chunk.get("type", "text"),
            })

        try:
            self.client.insert(collection_name=COLLECTION_NAME, data=data)
            logger.info(f"插入 {len(data)} 条向量到 {COLLECTION_NAME}")
            return len(data)
        except Exception as e:
            logger.error(f"Milvus插入失败: {e}")
            self._reconnect()
            self.client.insert(collection_name=COLLECTION_NAME, data=data)
            return len(data)

    def search(
        self,
        query_embedding: list[float],
        document_ids: Optional[list[str]] = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        self.ensure_collection()

        filter_expr = ""
        if document_ids:
            ids_str = ", ".join([f'"{did}"' for did in document_ids])
            filter_expr = f'document_id in [{ids_str}]'

        try:
            results = self.client.search(
                collection_name=COLLECTION_NAME,
                data=[query_embedding],
                limit=top_k,
                output_fields=["id", "content", "document_id", "section_id", "page", "type"],
                filter=filter_expr if filter_expr else None,
            )
        except Exception as e:
            logger.error(f"Milvus搜索失败: {e}")
            self._reconnect()
            results = self.client.search(
                collection_name=COLLECTION_NAME,
                data=[query_embedding],
                limit=top_k,
                output_fields=["id", "content", "document_id", "section_id", "page", "type"],
                filter=filter_expr if filter_expr else None,
            )

        search_results = []
        if results and results[0]:
            for hit in results[0]:
                entity = hit.get("entity", {})
                search_results.append({
                    "id": entity.get("id", ""),
                    "content": entity.get("content", ""),
                    "document_id": entity.get("document_id", ""),
                    "section_id": entity.get("section_id", ""),
                    "page": entity.get("page", 0),
                    "type": entity.get("type", ""),
                    "score": hit.get("distance", 0.0),
                })

        logger.info(f"向量搜索返回 {len(search_results)} 条结果")
        return search_results

    def delete_by_document(self, document_id: str) -> bool:
        try:
            self.client.delete(
                collection_name=COLLECTION_NAME,
                filter=f'document_id == "{document_id}"',
            )
            logger.info(f"删除文档 {document_id} 的所有向量")
            return True
        except Exception as e:
            logger.error(f"删除文档向量失败: {e}")
            return False

    def close(self):
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
            self._connected = False


milvus_client = MilvusClient()
