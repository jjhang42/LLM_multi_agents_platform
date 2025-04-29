import os
import httpx
from core.adapters.executor.llm_executor_base import LLMExecutorBase
import json

class ClaudeExecutorAdapter(LLMExecutorBase):
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.api_base = os.getenv("CLAUDE_API_BASE", "https://api.anthropic.com/v1")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")

    def get_name(self) -> str:
        return "claude"

    async def _query_claude(self, prompt: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.api_base}/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        # Claude 특유의 응답 포맷 대응
        text = data["content"][0]["text"] if "content" in data and data["content"] else ""
        return text

    async def run(self, task: dict) -> str:
        """Task를 실행하고 결과를 반환"""
        message = task.get("raw_message", "")
        return await self._query_claude(message)
