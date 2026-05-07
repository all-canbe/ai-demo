from langchain_community.retrievers import BM25Retriever, TFIDFRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional, Union
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class SimpleEnsembleRetriever:
    """简单的集成检索器实现"""
    def __init__(self, retrievers: List, weights: List[float]):
        self.retrievers = retrievers
        self.weights = weights

    def get_relevant_documents(self, query: str) -> List[Document]:
        results = {}
        
        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.get_relevant_documents(query)
            for doc in docs:
                doc_id = id(doc) if hasattr(doc, 'page_content') else str(doc)
                if doc_id not in results:
                    results[doc_id] = {'doc': doc, 'score': 0}
                results[doc_id]['score'] += weight

        sorted_results = sorted(results.values(), key=lambda x: x['score'], reverse=True)
        return [r['doc'] for r in sorted_results]

class HybridRetriever:
    def __init__(self, vector_retriever=None, graph_retriever=None):
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever
        self.bm25_retriever = None
        self.tfidf_retriever = None
        self.ensemble_retriever = None

    def init_bm25_retriever(self, documents: List[Document]):
        """初始化BM25检索器"""
        self.bm25_retriever = BM25Retriever.from_documents(documents)
        self.bm25_retriever.k = 5
        logger.info("BM25检索器已初始化")

    def init_tfidf_retriever(self, documents: List[Document]):
        """初始化TF-IDF检索器"""
        self.tfidf_retriever = TFIDFRetriever.from_documents(documents)
        self.tfidf_retriever.k = 5
        logger.info("TF-IDF检索器已初始化")

    def init_ensemble_retriever(self, weights: List[float] = None):
        """初始化集成检索器"""
        retrievers = []
        
        if self.vector_retriever:
            retrievers.append(self.vector_retriever)
        if self.bm25_retriever:
            retrievers.append(self.bm25_retriever)
        if self.tfidf_retriever:
            retrievers.append(self.tfidf_retriever)

        if not retrievers:
            raise ValueError("至少需要一个检索器")

        if weights is None:
            weights = [1.0 / len(retrievers)] * len(retrievers)

        self.ensemble_retriever = SimpleEnsembleRetriever(
            retrievers=retrievers,
            weights=weights
        )
        logger.info(f"集成检索器已初始化，检索器数量: {len(retrievers)}")

    def vector_search(self, query: str, k: int = 5) -> List[Document]:
        """向量检索"""
        if not self.vector_retriever:
            raise ValueError("向量检索器未初始化")
        return self.vector_retriever.get_relevant_documents(query)[:k]

    def graph_search(self, query: str) -> List[Dict[str, Any]]:
        """知识图谱检索"""
        if not self.graph_retriever:
            raise ValueError("知识图谱检索器未初始化")
        return self.graph_retriever.query_graph(query)

    def bm25_search(self, query: str, k: int = 5) -> List[Document]:
        """BM25检索"""
        if not self.bm25_retriever:
            raise ValueError("BM25检索器未初始化")
        return self.bm25_retriever.get_relevant_documents(query)[:k]

    def hybrid_search(self, query: str, k: int = 5) -> List[Document]:
        """混合检索（使用集成检索器）"""
        if not self.ensemble_retriever:
            raise ValueError("集成检索器未初始化")
        
        results = self.ensemble_retriever.get_relevant_documents(query)[:k]
        logger.info(f"混合检索完成，找到 {len(results)} 个结果")
        return results

    def custom_hybrid_search(self, query: str, k: int = 5) -> Dict[str, List[Union[Document, Dict]]]:
        """自定义混合检索，返回各检索器的结果"""
        results = {}

        if self.vector_retriever:
            results["vector"] = self.vector_search(query, k)
        
        if self.bm25_retriever:
            results["bm25"] = self.bm25_search(query, k)
        
        if self.graph_retriever:
            results["graph"] = self.graph_search(query)

        return results

    def rerank_results(self, query: str, results: List[Document], top_k: int = 3) -> List[Document]:
        """对检索结果进行重排序"""
        if not results:
            return []
        
        scored_results = []
        for doc in results:
            score = self._calculate_relevance(query, doc)
            scored_results.append((doc, score))
        
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_results[:top_k]]

    def _calculate_relevance(self, query: str, document: Document) -> float:
        """计算相关性分数（简单实现）"""
        query_tokens = set(query.lower().split())
        doc_tokens = set(document.page_content.lower().split())
        
        if not query_tokens:
            return 0.0
        
        intersection = query_tokens & doc_tokens
        return len(intersection) / len(query_tokens)

    @staticmethod
    def split_documents(texts: List[str], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
        """分割文档为小块"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        
        documents = []
        for text in texts:
            chunks = text_splitter.split_text(text)
            for i, chunk in enumerate(chunks):
                documents.append(Document(
                    page_content=chunk,
                    metadata={"chunk_index": i, "total_chunks": len(chunks)}
                ))
        
        logger.info(f"文档分割完成，共 {len(documents)} 个chunk")
        return documents
