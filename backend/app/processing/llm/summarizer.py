from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Dict, Any, Optional, Iterator
import logging

logger = logging.getLogger(__name__)

class DocumentSummarizer:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            streaming=True,
            temperature=0.3
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )

    def summarize(self, text: str, mode: str = "default") -> str:
        """生成文档摘要"""
        if not text.strip():
            return "文档内容为空"

        docs = self._split_text(text)
        logger.info(f"开始生成摘要，文本长度: {len(text)}, 分割为 {len(docs)} 个chunk")

        if mode == "map_reduce":
            summary = self._map_reduce_summarize(docs)
        elif mode == "refine":
            summary = self._refine_summarize(docs)
        else:
            summary = self._default_summarize(docs)

        logger.info(f"摘要生成完成，长度: {len(summary)}")
        return summary

    def summarize_stream(self, text: str) -> Iterator[str]:
        """流式生成摘要"""
        if not text.strip():
            yield "文档内容为空"
            return

        docs = self._split_text(text)
        
        if len(docs) == 1:
            for chunk in self._stream_single_summary(docs[0].page_content):
                yield chunk
        else:
            for chunk in self._stream_multi_summary(docs):
                yield chunk

    def _split_text(self, text: str) -> List[Document]:
        """将文本分割为Document块"""
        chunks = self.text_splitter.split_text(text)
        return [Document(page_content=chunk) for chunk in chunks]

    def _default_summarize(self, docs: List[Document]) -> str:
        """默认摘要方法（stuff）"""
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="stuff",
            verbose=False
        )
        return chain.run(docs)

    def _map_reduce_summarize(self, docs: List[Document]) -> str:
        """Map-Reduce摘要方法"""
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            verbose=False
        )
        return chain.run(docs)

    def _refine_summarize(self, docs: List[Document]) -> str:
        """Refine摘要方法"""
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="refine",
            verbose=False
        )
        return chain.run(docs)

    def _stream_single_summary(self, text: str) -> Iterator[str]:
        """流式生成单文档摘要"""
        prompt = f"""请对以下文本进行简明扼要的总结：

{text}

总结："""

        for chunk in self.llm.stream(prompt):
            if hasattr(chunk, 'content'):
                yield chunk.content

    def _stream_multi_summary(self, docs: List[Document]) -> Iterator[str]:
        """流式生成多文档摘要"""
        chunk_summaries = []
        
        for i, doc in enumerate(docs):
            yield f"正在处理第 {i+1}/{len(docs)} 部分...\n"
            summary = self._default_summarize([doc])
            chunk_summaries.append(summary)
            yield f"第 {i+1} 部分摘要完成\n"

        combined = "\n\n".join(chunk_summaries)
        yield "\n正在整合所有部分...\n"
        
        final_prompt = f"""请将以下多个摘要整合成一个连贯的最终摘要：

{combined}

最终总结："""

        for chunk in self.llm.stream(final_prompt):
            if hasattr(chunk, 'content'):
                yield chunk.content

    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """提取文档关键点"""
        prompt = f"""请从以下文本中提取最多 {max_points} 个关键点：

{text}

关键点："""

        result = self.llm.predict(prompt)
        points = [p.strip() for p in result.split("\n") if p.strip()]
        return points[:max_points]

    def generate_questions(self, text: str, max_questions: int = 5) -> List[str]:
        """基于文档内容生成问题"""
        prompt = f"""请基于以下文本内容生成最多 {max_questions} 个问题：

{text}

问题："""

        result = self.llm.predict(prompt)
        questions = [q.strip() for q in result.split("\n") if q.strip()]
        return questions[:max_questions]

    def summarize_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, str]:
        """批量总结多个文档"""
        results = {}
        for doc in documents:
            doc_id = doc.get("id", str(documents.index(doc)))
            content = doc.get("content", "")
            try:
                summary = self.summarize(content)
                results[doc_id] = summary
            except Exception as e:
                logger.error(f"文档 {doc_id} 摘要失败: {str(e)}")
                results[doc_id] = f"摘要失败: {str(e)}"
        return results

    def create_executive_summary(self, text: str) -> str:
        """生成执行摘要（更高级别的总结）"""
        prompt = f"""请为以下文档生成一份执行摘要，包括：
1. 核心内容概述
2. 关键发现或结论
3. 主要建议

文档内容：
{text}

执行摘要："""

        return self.llm.predict(prompt)

    def create_bullet_summary(self, text: str) -> str:
        """生成要点式摘要"""
        prompt = f"""请将以下文本转换为要点式摘要：

{text}

要点摘要："""

        return self.llm.predict(prompt)
