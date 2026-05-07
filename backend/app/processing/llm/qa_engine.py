from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
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
        self.retrieval_qa = None
        self.conversational_qa = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    def init_retrieval_qa(self, retriever, prompt_template: str = None):
        """初始化检索问答链"""
        if prompt_template is None:
            prompt_template = """使用以下上下文来回答用户的问题。如果你不知道答案，就说你不知道，不要编造答案。

上下文: {context}

问题: {question}

答案:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        self.retrieval_qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        logger.info("检索问答链已初始化")

    def init_conversational_qa(self, retriever):
        """初始化对话式问答链"""
        self.conversational_qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True
        )
        logger.info("对话式问答链已初始化")

    def answer(self, question: str) -> Dict[str, Any]:
        """非流式问答"""
        if not self.retrieval_qa:
            raise ValueError("检索问答链未初始化")

        result = self.retrieval_qa({"query": question})
        logger.info(f"问答完成，问题: {question[:50]}...")
        
        return {
            "answer": result["result"],
            "sources": [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in result.get("source_documents", [])
            ]
        }

    def answer_stream(self, question: str) -> Iterator[str]:
        """流式问答"""
        if not self.retrieval_qa:
            raise ValueError("检索问答链未初始化")

        logger.info(f"开始流式问答，问题: {question[:50]}...")
        
        for chunk in self._streaming_answer(question):
            yield chunk

    def _streaming_answer(self, question: str) -> Iterator[str]:
        """内部流式回答方法"""
        from langchain.callbacks import StreamingStdOutCallbackHandler
        from langchain.chains import LLMChain
        
        prompt = PromptTemplate(
            template="""使用以下上下文来回答用户的问题：

上下文: {context}

问题: {question}

答案:""",
            input_variables=["context", "question"]
        )

        docs = self.retrieval_qa.retriever.get_relevant_documents(question)
        context = "\n\n".join([doc.page_content for doc in docs])

        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            callbacks=[StreamingStdOutCallbackHandler()]
        )

        for chunk in chain.stream({"context": context, "question": question}):
            if "text" in chunk:
                yield chunk["text"]

    def conversational_answer(self, question: str) -> Dict[str, Any]:
        """对话式问答"""
        if not self.conversational_qa:
            raise ValueError("对话式问答链未初始化")

        result = self.conversational_qa({"question": question})
        logger.info(f"对话式问答完成")
        
        return {
            "answer": result["answer"],
            "sources": [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in result.get("source_documents", [])
            ],
            "chat_history": [str(msg) for msg in self.memory.chat_memory.messages]
        }

    def clear_history(self):
        """清除对话历史"""
        self.memory.clear()
        logger.info("对话历史已清除")

    def get_chat_history(self) -> List[str]:
        """获取对话历史"""
        return [str(msg) for msg in self.memory.chat_memory.messages]

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

        result = self.llm.predict(prompt)
        return result.strip()
