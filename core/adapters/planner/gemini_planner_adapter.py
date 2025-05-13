import os
import logging
import httpx
from typing import List, Dict, Any
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.system.formats.a2a_part import Part
from core.system.utils.chat_task_builder import make_chat_response_task
from core.system.memory.SessionMessageMemory import SessionMessageMemory

logger = logging.getLogger(__name__)


class GeminiPlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.api_base = os.getenv("ORCHESTRATOR_GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta")
        self.model = os.getenv("ORCHESTRATOR_GEMINI_MODEL", "models/gemini-pro")

        if not self.api_key:
            raise ValueError("❌ 환경 변수 'ORCHESTRATOR_GEMINI_API_KEY' 또는 'GEMINI_API_KEY'가 설정되지 않았습니다.")

    async def _call_llm_with_parts(self, context: Dict[str, Any]) -> str:
        parts = context.get("parts", [])
        agent_cards = context.get("agent_cards", [])
        prior_tasks = context.get("prior_tasks", [])
        context_id = context.get("context_id", "default")

        user_text = next((p.text for p in parts if getattr(p, "type", "") == "text"), "")
        SessionMessageMemory.append(context_id, "user", user_text)

        agent_skill_ids = []
        for card in agent_cards:
            card_id = getattr(card, "id", "unknown")
            skills = getattr(card, "skills", [])
            logger.debug(f"[GeminiPlanner] AgentCard ID={card_id} has {len(skills)} skill(s).")
            for skill in skills:
                skill_id = getattr(skill, "id", "undefined")
                logger.debug(f"[GeminiPlanner] - Skill ID: {skill_id}")
                agent_skill_ids.append(skill_id)

        prior_task_ids = [t.get("id", "task") for t in prior_tasks]
        prior_messages = SessionMessageMemory.get(context_id)[-10:]

        prompt = f"""
[사용자 요청]
{user_text}

[대화 히스토리]
{chr(10).join(f"{m['role']}: {m['text']}" for m in prior_messages)}

[사용 가능 에이전트 스킬 ID 목록]
{agent_skill_ids}

[이전 작업들]
{prior_task_ids}

위 정보를 바탕으로 JSON 형식의 A2A Task 목록과 DAG 의존 그래프를 생성해주세요.
""".strip()

        logger.info(f"[GeminiPlanner] LLM Prompt 준비 완료. 총 skill {len(agent_skill_ids)}개.")
        response_text = await self._send_to_gemini(prompt)

        SessionMessageMemory.append(context_id, "assistant", response_text)
        return response_text

    async def _chat_response(self, parts: List[Part], context_id: str = "default"):
        user_text = next((p.text for p in parts if getattr(p, "type", "") == "text"), "")
        SessionMessageMemory.append(context_id, "user", user_text)

        prior_messages = SessionMessageMemory.get(context_id)[-10:]
        prompt = f"""
[이전 대화 히스토리]
{chr(10).join(f"{m['role']}: {m['text']}" for m in prior_messages)}

[현재 사용자 메시지]
{user_text}

자연스럽고 간결하게 응답해줘.
""".strip()

        logger.debug(f"[GeminiPlanner] Chat response prompt: {prompt}")
        response_text = await self._send_to_gemini(prompt)
        SessionMessageMemory.append(context_id, "assistant", response_text)

        return make_chat_response_task(response_text)

    async def generate_natural_language(self, task: dict) -> str:
        action = task.get('metadata', {}).get('action', '작업')
        return f"{action} 작업을 수행합니다."

    async def _send_to_gemini(self, prompt: str) -> str:
        url = f"{self.api_base}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        logger.debug(f"[GeminiPlanner] 요청 전송 중... URL: {url}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"[GeminiPlanner] HTTP 오류 발생: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"[GeminiPlanner] 예금치 않은 오류 발생: {e}")
            raise

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"[GeminiPlanner] 응답 파싱 실패: {e}\n전체 응답: {data}")
            raise RuntimeError(f"[GeminiPlanner] 응답 파싱 실패: {e}")