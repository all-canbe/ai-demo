from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from typing import List, Dict, Any, Optional, Iterator
import logging

logger = logging.getLogger(__name__)

class QAEngine:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            streaming=True,
            temperature=0.7
        )
        self.chat_history = []
        self.retriever = None

    def init_retrieval_qa(self, retriever, prompt_template: str = None):
        """初始化检索问答"""
        self.retriever = retriever
        logger.info("检索问答已初始化")

    def init_conversational_qa(self, retriever):
        """初始化对话式问答"""
        self.retriever = retriever
        logger.info("对话式问答已初始化")

    def generate_answer(self, question: str, context: str = "") -> str:
        """生成回答"""
        if context:
            prompt = f"""使用以下上下文来回答用户的问题。如果你不知道答案，就说你不知道，不要编造答案。

上下文: {context}

问题: {question}

答案:"""
        else:
            prompt = f"""回答以下问题：

问题: {question}

答案:"""

        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        return response.content.strip()

    def answer(self, question: str) -> Dict[str, Any]:
        """非流式问答"""
        if not self.retriever:
            raise ValueError("检索器未初始化")

        docs = self.retriever.get_relevant_documents(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = f"""使用以下上下文来回答用户的问题。如果你不知道答案，就说你不知道，不要编造答案。

上下文: {context}

问题: {question}

答案:"""

        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        logger.info(f"问答完成，问题: {question[:50]}...")
        
        return {
            "answer": response.content.strip(),
            "sources": [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in docs
            ]
        }

    def answer_stream(self, question: str) -> Iterator[str]:
        """流式问答"""
        if not self.retriever:
            raise ValueError("检索器未初始化")

        logger.info(f"开始流式问答，问题: {question[:50]}...")
        
        docs = self.retriever.get_relevant_documents(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = f"""使用以下上下文来回答用户的问题：

上下文: {context}

问题: {question}

答案:"""

        messages = [HumanMessage(content=prompt)]
        
        for chunk in self.llm.stream(messages):
            if hasattr(chunk, 'content'):
                yield chunk.content

    def conversational_answer(self, question: str) -> Dict[str, Any]:
        """对话式问答"""
        if not self.retriever:
            raise ValueError("检索器未初始化")

        docs = self.retriever.get_relevant_documents(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        messages = []
        for msg in self.chat_history:
            messages.append(msg)
        
        messages.append(HumanMessage(content=f"""使用以下上下文来回答问题：

上下文: {context}

问题: {question}
"""))

        response = self.llm.invoke(messages)
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=response.content))
        
        logger.info(f"对话式问答完成")
        
        return {
            "answer": response.content.strip(),
            "sources": [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in docs
            ],
            "chat_history": [str(msg.content) for msg in self.chat_history]
        }

    def clear_history(self):
        """清除对话历史"""
        self.chat_history = []
        logger.info("对话历史已清除")

    def get_chat_history(self) -> List[str]:
        """获取对话历史"""
        return [str(msg.content) for msg in self.chat_history]

    def batch_answer(self, questions: List[str]) -> List[Dict[str, Any]]:
        """批量问答"""
        results = []
        for question in questions:
            try:
                result = self.answer(question)
                results.append({"question": question, **result})
            except Exception as e:
                logger.error(f"批量问答失败，问题: {question}: {str(e)}")
                results.append({"question": question, "error": str(e)})
        return results

    def summarize_conversation(self) -> str:
        """总结对话"""
        history = self.get_chat_history()
        if not history:
            return "对话历史为空"

        prompt = f"""总结以下对话内容：

{chr(10).join(history)}

总结:"""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
