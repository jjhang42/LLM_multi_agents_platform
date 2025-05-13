import os
import httpx
import uuid
import json
from typing import List, Dict, Any
from string import Template

from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.system.formats.a2a_part import Part
from core.system.utils.chat_task_builder import make_chat_response_task
from core.prompts.loader import load_prompt


class ClaudePlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_CLAUDE_API_KEY", os.getenv("CLAUDE_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_CLAUDE_API_BASE", "https://api.anthropic.com/v1")
        self.model = os.getenv("ORCHESTRATOR_CLAUDE_MODEL", "claude-3-opus-20240229")

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

        if not self.api_key:
            raise ValueError("❌ 환경 변수 'CLAUDE_API_KEY' 또는 'ORCHESTRATOR_CLAUDE_API_KEY'가 필요합니다.")

    async def _call_llm_with_parts(self, context: Dict[str, Any]) -> str:
        parts = context.get("parts", [])
        agent_cards = context.get("agent_cards", [])
        prior_tasks = context.get("prior_tasks", [])

        user_text = next((p.text for p in parts if p.type == "text"), "")
        agent_skill_ids = [card.get("id", "unknown") for card in agent_cards]
        prior_task_ids = [t.get("id", "task") for t in prior_tasks]

        prompt = f"""
{self.prompt_parse_task.strip()}

[사용자 요청]
{user_text}

[사용 가능 에이전트 스킬 ID 목록]
{agent_skill_ids}

[이전 작업들]
{prior_task_ids}
        """.strip()

        return await self._send_claude_prompt(prompt)

    async def _chat_response(self, parts: List[Part]):
        user_text = next((p.text for p in parts if p.type == "text"), "")
        prompt = f"다음 사용자 메시지에 짧고 자연스럽게 응답해주세요:\n\n\"{user_text}\""
        response = await self._send_claude_prompt(prompt)
        return make_chat_response_task(response)

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

        # 디버깅용 응답 저장 (선택적)
        if os.getenv("DEBUG_SAVE_LLM_RESPONSE", "false").lower() == "true":
            path = f"/tmp/claude_response_{uuid.uuid4().hex[:8]}.json"
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"📁 Claude 응답 저장됨: {path}")

        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"[ClaudePlanner] 응답 파싱 실패: {e}\n전체 응답: {data}")
