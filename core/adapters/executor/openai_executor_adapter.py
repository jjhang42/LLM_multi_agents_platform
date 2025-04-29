import os
import httpx
from core.adapters.executor.llm_executor_base import LLMExecutorBase
import json

class OpenAIExecutorAdapter(LLMExecutorBase):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def get_name(self) -> str:
        return "openai"

    async def _query_openai(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.api_base}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        text = data["choices"][0]["message"]["content"]
        return text

    async def run(self, task: dict) -> str:
        """Task를 실행하고 결과를 반환"""
        message = task.get("raw_message", "")
        return await self._query_openai(message)
