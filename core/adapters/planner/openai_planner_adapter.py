import os
import httpx
import json
from string import Template  # ✅ 추가
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt
from core.system.metadata.task_graph import TaskGraph

class OpenAIPlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_OPENAI_API_BASE", os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
        self.model = os.getenv("ORCHESTRATOR_OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_transform_task = load_prompt("planner_transform_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

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

    async def parse(self, input_text: str) -> tuple[dict, TaskGraph]:
        """자연어 → tasks + graph"""
        prompt = Template(self.prompt_parse_task).substitute(input_text=input_text)  # ✅ Template 사용
        result_text = await self._query_openai(prompt)

        try:
            parsed = json.loads(result_text)
        except Exception:
            return {"error": "Failed to parse Task JSON", "raw": result_text}, TaskGraph()

        tasks = {}
        graph = TaskGraph()

        if isinstance(parsed, dict):
            task_id = parsed.get("id", "task_root")
            tasks[task_id] = parsed
            graph.add_task(task_id)
        elif isinstance(parsed, list):
            for task in parsed:
                task_id = task.get("id")
                if not task_id:
                    continue
                tasks[task_id] = task
                graph.add_task(task_id)
        else:
            return {"error": "Invalid format", "raw": result_text}, TaskGraph()

        return tasks, graph

    async def generate_natural_language(self, task: dict) -> str:
        task_text = json.dumps(task, ensure_ascii=False)
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)  # ✅ Template 사용
        return await self._query_openai(prompt)
