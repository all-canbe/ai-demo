from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)
from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MilvusVectorStore:
    def __init__(self, host: str, port: int, collection_name: str):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings()
        self.client = None
        self.collection = None

    def connect(self):
        """连接Milvus服务器"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            self.client = connections.get_connection("default")
            logger.info(f"成功连接Milvus服务器: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"连接Milvus失败: {str(e)}")
            raise

    def create_collection(self, dimension: int = 1536):
        """创建向量集合"""
        try:
            if utility.has_collection(self.collection_name):
                logger.warning(f"集合 {self.collection_name} 已存在，将删除重建")
                utility.drop_collection(self.collection_name)

            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="chunk_index", dtype=DataType.INT64)
            ]

            schema = CollectionSchema(fields, description="文档向量存储")
            self.collection = Collection(name=self.collection_name, schema=schema)

            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            self.collection.create_index("vector", index_params)
            logger.info(f"成功创建集合: {self.collection_name}")
        except Exception as e:
            logger.error(f"创建集合失败: {str(e)}")
            raise

    def load_collection(self):
        """加载集合到内存"""
        if self.collection is None:
            self.collection = Collection(self.collection_name)
        self.collection.load()
        logger.info(f"集合 {self.collection_name} 已加载")

    def add_documents(self, texts: List[str], metadatas: Optional[List[Dict]] = None):
        """向量化并添加文档"""
        try:
            if not texts:
                return []

            if metadatas is None:
                metadatas = [{} for _ in texts]

            vectors = self.embeddings.embed_documents(texts)
            
            entities = []
            for i, (text, metadata) in enumerate(zip(texts, metadatas)):
                entities.append({
                    "vector": vectors[i],
                    "content": text,
                    "metadata": str(metadata),
                    "file_name": metadata.get("file_name", ""),
                    "chunk_index": metadata.get("chunk_index", i)
                })

            result = self.collection.insert(entities)
            self.collection.flush()
            logger.info(f"成功插入 {len(texts)} 条文档向量")
            return result.primary_keys
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """向量相似性搜索"""
        try:
            query_vector = self.embeddings.embed_query(query)
            
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }

            results = self.collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=k,
                expr=None,
                output_fields=["content", "metadata", "file_name", "chunk_index"]
            )

            matches = []
            for hit in results[0]:
                matches.append({
                    "id": hit.id,
                    "score": hit.distance,
                    "content": hit.entity.get("content"),
                    "metadata": hit.entity.get("metadata"),
                    "file_name": hit.entity.get("file_name"),
                    "chunk_index": hit.entity.get("chunk_index")
                })

            logger.info(f"搜索完成，找到 {len(matches)} 个匹配结果")
            return matches
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise

    def get_langchain_retriever(self, search_kwargs: Dict = None):
        """获取LangChain格式的检索器"""
        if search_kwargs is None:
            search_kwargs = {"k": 5}

        vector_store = Milvus(
            embedding_function=self.embeddings,
            connection_args={"host": self.host, "port": self.port},
            collection_name=self.collection_name
        )
        return vector_store.as_retriever(search_kwargs=search_kwargs)

    def delete_collection(self):
        """删除集合"""
        try:
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                logger.info(f"已删除集合: {self.collection_name}")
        except Exception as e:
            logger.error(f"删除集合失败: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            if self.collection is None:
                self.collection = Collection(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "total_entities": self.collection.num_entities,
                "index_building": self.collection.has_index()
            }
        except Exception as e:
            logger.error(f"获取集合统计失败: {str(e)}")
            raise

    def close(self):
        """关闭连接"""
        try:
            if self.collection:
                self.collection.release()
            connections.disconnect("default")
            logger.info("已关闭Milvus连接")
        except Exception as e:
            logger.error(f"关闭连接失败: {str(e)}")
