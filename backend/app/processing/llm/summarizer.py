from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
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

        chunks = self.text_splitter.split_text(text)
        logger.info(f"开始生成摘要，文本长度: {len(text)}, 分割为 {len(chunks)} 个chunk")

        if len(chunks) == 1:
            summary = self._summarize_single(chunks[0])
        else:
            if mode == "map_reduce":
                summary = self._map_reduce_summarize(chunks)
            elif mode == "refine":
                summary = self._refine_summarize(chunks)
            else:
                summary = self._default_summarize(chunks)

        logger.info(f"摘要生成完成，长度: {len(summary)}")
        return summary

    def summarize_stream(self, text: str) -> Iterator[str]:
        """流式生成摘要"""
        if not text.strip():
            yield "文档内容为空"
            return

        chunks = self.text_splitter.split_text(text)
        
        if len(chunks) == 1:
            for chunk in self._stream_single_summary(chunks[0]):
                yield chunk
        else:
            for chunk in self._stream_multi_summary(chunks):
                yield chunk

    def _summarize_single(self, text: str) -> str:
        """总结单块文本"""
        prompt = f"""请对以下文本进行简明扼要的总结：

{text}

总结："""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def _default_summarize(self, chunks: List[str]) -> str:
        """默认摘要方法"""
        combined = "\n\n".join(chunks[:3])
        if len(chunks) > 3:
            combined = combined + "\n\n（...更多内容省略）"
        
        prompt = f"""请对以下文本进行简明扼要的总结：

{combined}

总结："""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def _map_reduce_summarize(self, chunks: List[str]) -> str:
        """Map-Reduce摘要方法"""
        chunk_summaries = []
        for chunk in chunks:
            summary = self._summarize_single(chunk)
            chunk_summaries.append(summary)
        
        combined = "\n\n".join(chunk_summaries)
        final_prompt = f"""请将以下多个摘要整合成一个连贯的最终摘要：

{combined}

最终总结："""

        response = self.llm.invoke([HumanMessage(content=final_prompt)])
        return response.content.strip()

    def _refine_summarize(self, chunks: List[str]) -> str:
        """Refine摘要方法"""
        summary = self._summarize_single(chunks[0])
        
        for i in range(1, len(chunks)):
            refine_prompt = f"""基于以下已有的总结：

{summary}

请结合新增的内容进行补充和改进：

{chunks[i]}

改进后的总结："""
            
            response = self.llm.invoke([HumanMessage(content=refine_prompt)])
            summary = response.content.strip()
        
        return summary

    def _stream_single_summary(self, text: str) -> Iterator[str]:
        """流式生成单文档摘要"""
        prompt = f"""请对以下文本进行简明扼要的总结：

{text}

总结："""

        for chunk in self.llm.stream([HumanMessage(content=prompt)]):
            if hasattr(chunk, 'content'):
                yield chunk.content

    def _stream_multi_summary(self, chunks: List[str]) -> Iterator[str]:
        """流式生成多文档摘要"""
        chunk_summaries = []
        
        for i, chunk in enumerate(chunks):
            yield f"正在处理第 {i+1}/{len(chunks)} 部分...\n"
            summary = self._summarize_single(chunk)
            chunk_summaries.append(summary)
            yield f"第 {i+1} 部分摘要完成\n"

        combined = "\n\n".join(chunk_summaries)
        yield "\n正在整合所有部分...\n"
        
        final_prompt = f"""请将以下多个摘要整合成一个连贯的最终摘要：

{combined}

最终总结："""

        for chunk in self.llm.stream([HumanMessage(content=final_prompt)]):
            if hasattr(chunk, 'content'):
                yield chunk.content

    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """提取文档关键点"""
        prompt = f"""请从以下文本中提取最多 {max_points} 个关键点：

{text}

关键点："""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        points = [p.strip() for p in response.content.split("\n") if p.strip()]
        return points[:max_points]

    def generate_questions(self, text: str, max_questions: int = 5) -> List[str]:
        """基于文档内容生成问题"""
        prompt = f"""请基于以下文本内容生成最多 {max_questions} 个问题：

{text}

问题："""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        questions = [q.strip() for q in response.content.split("\n") if q.strip()]
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

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def create_bullet_summary(self, text: str) -> str:
        """生成要点式摘要"""
        prompt = f"""请将以下文本转换为要点式摘要：

{text}

要点摘要："""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
