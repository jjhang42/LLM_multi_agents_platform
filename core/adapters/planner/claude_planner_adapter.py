import os
import httpx
import json
from string import Template
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt
from core.system.metadata.task_graph import TaskGraph

class ClaudePlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_CLAUDE_API_KEY", os.getenv("CLAUDE_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_CLAUDE_API_BASE", os.getenv("CLAUDE_API_BASE", "https://api.anthropic.com/v1"))
        self.model = os.getenv("ORCHESTRATOR_CLAUDE_MODEL", os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229"))

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_transform_task = load_prompt("planner_transform_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

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

        text = data["content"][0]["text"] if "content" in data and data["content"] else ""
        return text

    async def parse(self, input_text: str) -> tuple[dict, TaskGraph]:
        """자연어 → tasks + graph"""
        prompt = Template(self.prompt_parse_task).substitute(input_text=input_text)  # ✅ Template 적용
        result_text = await self._query_claude(prompt)
    
        try:
            parsed = json.loads(result_text)
        except Exception:
            return {"error": "Failed to parse Task JSON", "raw": result_text}, TaskGraph()
    
        tasks = {}
        graph = TaskGraph()
    
        # ✅ 단일 Task / 복수 Task 모두 대응
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
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)  # ✅ Template 적용
        return await self._query_claude(prompt)
