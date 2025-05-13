import os
import httpx
import uuid
import json
from typing import List, Dict, Any
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.system.formats.a2a_part import Part
from core.system.utils.chat_task_builder import make_chat_response_task


class OpenAIPlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model = os.getenv("ORCHESTRATOR_OPENAI_MODEL", "gpt-4")

        if not self.api_key:
            raise ValueError("❌ 환경 변수 'ORCHESTRATOR_OPENAI_API_KEY' 또는 'OPENAI_API_KEY'가 설정되지 않았습니다.")

    async def _call_llm_with_parts(self, context: Dict[str, Any]) -> str:
        parts = context.get("parts", [])
        agent_cards = context.get("agent_cards", [])
        prior_tasks = context.get("prior_tasks", [])

        user_text = next((p.text for p in parts if p.type == "text"), "")
        agent_skill_ids = [card.get("id", "unknown") for card in agent_cards]
        prior_task_ids = [t.get("id", "task") for t in prior_tasks]

        system_prompt = "너는 A2A Task Planner야. 사용자 요청을 받아 JSON 형식의 Task와 그래프를 생성해."
        user_prompt = f"""
[사용자 요청]
{user_text}

[사용 가능 에이전트 스킬 ID 목록]
{agent_skill_ids}

[이전 작업들]
{prior_task_ids}

JSON 형식의 A2A Task 목록과 DAG 의존 그래프를 생성해줘.
""".strip()

        return await self._send_to_openai(system_prompt, user_prompt)

    async def _chat_response(self, parts: List[Part]):
        user_text = next((p.text for p in parts if p.type == "text"), "")
        system_prompt = "친절하고 짧은 AI 비서로 응답해주세요."
        user_prompt = f"{user_text}"

        response_text = await self._send_to_openai(system_prompt, user_prompt)
        return make_chat_response_task(response_text)

    async def generate_natural_language(self, task: dict) -> str:
        return f"{task.get('metadata', {}).get('action', '작업')} 작업을 수행합니다."

    async def _send_to_openai(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"[OpenAIPlanner] 응답 파싱 실패: {e}\n전체 응답: {data}")
