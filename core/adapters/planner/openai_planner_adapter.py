import os
import httpx
from string import Template
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt

class OpenAIPlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_OPENAI_API_BASE", os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
        self.model = os.getenv("ORCHESTRATOR_OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

    async def _call_llm(self, input_text: str) -> str:
        prompt = Template(self.prompt_parse_task).substitute(input_text=input_text)
        return await self._query_openai(prompt)

    async def _query_openai(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a task parsing and planning assistant. Respond strictly in JSON format."},
                {"role": "user", "content": prompt}
            ]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.api_base}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

    async def generate_natural_language(self, task: dict) -> str:
        task_text = str(task)
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)
        return await self._query_openai(prompt)
