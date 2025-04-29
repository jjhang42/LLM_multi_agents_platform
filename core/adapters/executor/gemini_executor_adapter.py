import os
import httpx
from core.adapters.executor.llm_executor_base import LLMExecutorBase
import json

class GeminiExecutorAdapter(LLMExecutorBase):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.api_base = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta")
        self.model = os.getenv("GEMINI_MODEL", "models/gemini-pro")

    def get_name(self) -> str:
        return "gemini"

    async def _query_gemini(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        url = f"{self.api_base}/{self.model}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text

    async def run(self, task: dict) -> str:
        """Task를 실행하고 결과를 반환"""
        message = task.get("raw_message", "")
        return await self._query_gemini(message)
