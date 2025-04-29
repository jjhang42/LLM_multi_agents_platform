import os
import httpx
import json
import uuid
from typing import Dict, Tuple
from string import Template  # ✅ 추가
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt
from core.system.metadata.task_graph import TaskGraph

class GeminiPlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_GEMINI_API_BASE", os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta"))
        self.model = os.getenv("ORCHESTRATOR_GEMINI_MODEL", os.getenv("GEMINI_MODEL", "models/gemini-pro"))

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_transform_task = load_prompt("planner_transform_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

    async def _query_gemini(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        url = f"{self.api_base}/{self.model}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _parse_single_task(self, input_text: str) -> dict:
        """자연어 → 단일 Task 변환"""
        prompt = Template(self.prompt_parse_task).substitute(input_text=input_text)  # ✅ Template 적용
        result_text = await self._query_gemini(prompt)
        try:
            return json.loads(result_text)
        except Exception:
            return {"error": "Failed to parse Task JSON", "raw": result_text}

    async def parse(self, input_text: str) -> Tuple[Dict[str, dict], TaskGraph]:
        """LLMPlannerBase 명세 충족: 자연어 → Tasks + Graph"""
        task = await self._parse_single_task(input_text)

        task_id = task.get("id") or str(uuid.uuid4())
        tasks = {task_id: task}

        graph = TaskGraph()
        graph.add_task(task_id)

        return tasks, graph

    async def transform_task(self, task: dict) -> dict:
        """기존 Task를 기반으로 다음 Task 생성"""
        task_text = json.dumps(task, ensure_ascii=False)
        prompt = Template(self.prompt_transform_task).substitute(task_text=task_text)  # ✅ Template 적용
        result_text = await self._query_gemini(prompt)
        try:
            return json.loads(result_text)
        except Exception:
            return {"error": "Failed to transform Task JSON", "raw": result_text}

    async def generate_natural_language(self, task: dict) -> str:
        """Task를 자연어 설명으로 변환"""
        task_text = json.dumps(task, ensure_ascii=False)
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)  # ✅ Template 적용
        result_text = await self._query_gemini(prompt)
        return result_text
