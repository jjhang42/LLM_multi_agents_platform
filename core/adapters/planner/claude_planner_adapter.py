import os
import httpx
import uuid
import json
from string import Template
from typing import List
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt
from core.system.formats.a2a_part import Part, TextPart


class ClaudePlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_CLAUDE_API_KEY", os.getenv("CLAUDE_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_CLAUDE_API_BASE", os.getenv("CLAUDE_API_BASE", "https://api.anthropic.com/v1"))
        self.model = os.getenv("ORCHESTRATOR_CLAUDE_MODEL", os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229"))

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

    async def _call_llm_with_parts(self, parts: List[Part]) -> str:
        # 프롬프트 + parts[]를 텍스트로 직렬화
        content = self.prompt_parse_task.strip() + "\n\n"
        for part in parts:
            if part.type == "text":
                content += f"[Text]\n{part.text}\n"
            elif part.type == "file":
                uri = getattr(part.file, "uri", "unknown")
                name = getattr(part.file, "name", "unnamed")
                content += f"[File: {name}]\n{uri}\n"
            elif hasattr(part, "url"):
                content += f"[{part.type.upper()}]\n{part.url}\n"

        return await self._send_claude_prompt(content)

    async def generate_natural_language(self, task: dict) -> str:
        task_text = str(task)
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)
        return await self._send_claude_prompt(prompt)

    async def _send_claude_prompt(self, prompt: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:            
            response = await client.post(f"{self.api_base}/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        # 디버깅 응답 저장
        if os.getenv("DEBUG_SAVE_LLM_RESPONSE", "false").lower() == "true":
            path = f"/tmp/claude_response_{uuid.uuid4().hex[:8]}.json"
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Claude 응답 저장됨: {path}")

        # 안전한 응답 추출
        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"[ClaudePlanner] 응답 파싱 실패: {e}\n전체 응답: {data}")
