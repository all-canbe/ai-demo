from typing import List, Dict, Any
import uuid
import logging

from app.processing.document.parser import DocumentParser
from app.processing.vector.milvus_store import MilvusVectorStore
from app.processing.graph.neo4j_graph import Neo4jGraphBuilder
from app.processing.retrieval.hybrid_retriever import HybridRetriever
from app.processing.llm.qa_engine import QAEngine
from app.processing.llm.summarizer import DocumentSummarizer
from app.config.settings import settings

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.parser = DocumentParser(settings.TESSERACT_PATH)
        self.vector_store = MilvusVectorStore(
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            collection_name=settings.MILVUS_COLLECTION
        )
        self.graph_builder = Neo4jGraphBuilder(
            uri=settings.NEO4J_URI,
            username=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )
        self.qa_engine = QAEngine(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.summarizer = DocumentSummarizer(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.hybrid_retriever = HybridRetriever()
        
        self._initialized = False

    def initialize(self):
        """初始化所有服务"""
        if self._initialized:
            return
        
        logger.info("初始化文档处理服务...")
        
        try:
            self.vector_store.connect()
            self.vector_store.create_collection()
            self.vector_store.load_collection()
        except Exception as e:
            logger.warning(f"Milvus初始化失败（可能未启动）: {str(e)}")
        
        try:
            self.graph_builder.connect()
        except Exception as e:
            logger.warning(f"Neo4j初始化失败（可能未启动）: {str(e)}")
        
        self._initialized = True
        logger.info("文档处理服务初始化完成")

    def process_document(self, filename: str, file_content: bytes) -> Dict[str, Any]:
        """处理文档：解析、向量化、构建图谱"""
        document_id = str(uuid.uuid4())
        
        parsed = self.parser.parse(filename, file_content)
        logger.info(f"文档解析完成: {document_id}")
        
        text = self._extract_text_from_parsed(parsed)
        
        metadatas = []
        chunks = self.hybrid_retriever.split_documents([text])
        for i, chunk in enumerate(chunks):
            metadatas.append({
                "document_id": document_id,
                "file_name": filename,
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
        
        try:
            vector_ids = self.vector_store.add_documents(
                [chunk.page_content for chunk in chunks],
                metadatas
            )
            logger.info(f"向量存储完成，ID: {vector_ids}")
        except Exception as e:
            logger.warning(f"向量存储失败: {str(e)}")
            vector_ids = []
        
        try:
            graph_result = self.graph_builder.build_knowledge_graph(
                document_id=document_id,
                content=text,
                metadata={"file_name": filename}
            )
            logger.info(f"知识图谱构建完成: {graph_result}")
        except Exception as e:
            logger.warning(f"知识图谱构建失败: {str(e)}")
            graph_result = {}
        
        return {
            "document_id": document_id,
            "filename": filename,
            "text_length": len(text),
            "chunks_count": len(chunks),
            "vector_ids": vector_ids,
            "graph_result": graph_result
        }

    def _extract_text_from_parsed(self, parsed) -> str:
        """从解析结果中提取纯文本"""
        if isinstance(parsed, list):
            if all(isinstance(item, dict) and "text" in item for item in parsed):
                return "\n\n".join(item["text"] for item in parsed)
        elif isinstance(parsed, dict):
            if "text" in parsed:
                return parsed["text"]
            elif "paragraphs" in parsed:
                return "\n\n".join(p["text"] for p in parsed["paragraphs"])
        
        return str(parsed)

    def query(self, question: str, use_streaming: bool = False):
        """查询问答"""
        if not self._initialized:
            self.initialize()
        
        try:
            self.hybrid_retriever.vector_retriever = self.vector_store.get_langchain_retriever()
            self.qa_engine.init_retrieval_qa(self.hybrid_retriever.vector_retriever)
            
            if use_streaming:
                return self.qa_engine.answer_stream(question)
            else:
                return self.qa_engine.answer(question)
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            raise

    def summarize(self, text: str, mode: str = "default", use_streaming: bool = False):
        """生成摘要"""
        if use_streaming:
            return self.summarizer.summarize_stream(text)
        else:
            return self.summarizer.summarize(text, mode)

    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """提取关键点"""
        return self.summarizer.extract_key_points(text, max_points)

    def get_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        stats = {
            "vector_store": {},
            "graph": {}
        }
        
        try:
            stats["vector_store"] = self.vector_store.get_collection_stats()
        except Exception as e:
            stats["vector_store"]["error"] = str(e)
        
        try:
            stats["graph"] = self.graph_builder.get_graph_stats()
        except Exception as e:
            stats["graph"]["error"] = str(e)
        
        return stats

document_service = DocumentService()
