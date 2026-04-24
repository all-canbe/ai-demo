from typing import AsyncIterator, Optional
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self):
        self._client = None
        self._model = settings.OPENAI_CHAT_MODEL

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
        return self._client

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        content = response.choices[0].message.content
        logger.info(f"LLM生成完成, tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
        return content

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        from openai import AsyncOpenAI

        async_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await async_client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        content = response.choices[0].message.content
        await async_client.close()
        return content

    async def agenerate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncIterator[str]:
        from openai import AsyncOpenAI

        async_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = await async_client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

        await async_client.close()


llm_service = LLMService()
