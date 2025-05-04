import os
import httpx
from string import Template
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt

class ClaudePlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_CLAUDE_API_KEY", os.getenv("CLAUDE_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_CLAUDE_API_BASE", os.getenv("CLAUDE_API_BASE", "https://api.anthropic.com/v1"))
        self.model = os.getenv("ORCHESTRATOR_CLAUDE_MODEL", os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229"))

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

    async def _call_llm(self, input_text: str) -> str:
        prompt = Template(self.prompt_parse_task).substitute(input_text=input_text)
        return await self._query_claude(prompt)

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

        return data["content"][0]["text"] if "content" in data and data["content"] else ""

    async def generate_natural_language(self, task: dict) -> str:
        task_text = str(task)
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)
        return await self._query_claude(prompt)