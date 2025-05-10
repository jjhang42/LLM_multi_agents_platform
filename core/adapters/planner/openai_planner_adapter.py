import os
import httpx
import uuid
import json
from string import Template
from typing import List
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt
from core.system.formats.a2a_part import Part, TextPart, FilePart

class OpenAIPlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_OPENAI_API_BASE", os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
        self.model = os.getenv("ORCHESTRATOR_OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4"))

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

    async def _call_llm_with_parts(self, parts: List[Part]) -> str:
        content = self.prompt_parse_task.strip() + "\n\n"
        for part in parts:
            if part.type == "text":
                content += f"[Text]\n{part.text}\n"
            elif part.type == "file" and isinstance(part, FilePart):
                uri = getattr(part.file, "uri", "unknown")
                name = getattr(part.file, "name", "unnamed")
                content += f"[File: {name}]\n{uri}\n"
            elif hasattr(part, "url"):
                content += f"[{part.type.upper()}]\n{part.url}\n"

        return await self._send_openai_prompt(content)

    async def generate_natural_language(self, task: dict) -> str:
        task_text = str(task)
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)
        return await self._send_openai_prompt(prompt)

    async def _send_openai_prompt(self, prompt: str) -> str:
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

        url = f"{self.api_base}/chat/completions"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        # 디버깅 응답 저장
        if os.getenv("DEBUG_SAVE_LLM_RESPONSE", "false").lower() == "true":
            path = f"/tmp/openai_response_{uuid.uuid4().hex[:8]}.json"
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"💾 OpenAI 응답 저장됨: {path}")

        # 안정적인 파싱
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"[OpenAIPlanner] 응답 파싱 실패: {e}\n전체 응답: {data}")
