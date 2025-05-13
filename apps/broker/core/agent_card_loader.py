# core/system/agent_card_loader.py

import os
import httpx
import asyncio
import logging
import random
from typing import Dict, List, Optional
from dotenv import load_dotenv
from core.system.formats.agent_card import AgentCard
from core.system.agent_registry import load_agent_registry

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

# 재시도 설정
RETRY_COUNT = int(os.getenv("AGENT_CARD_RETRY_COUNT", 6))
RETRY_DELAY = float(os.getenv("AGENT_CARD_RETRY_DELAY", 10.0))


class AgentCardLoader:
    def __init__(self):
        self.cards: Dict[str, List[AgentCard]] = {}
        self.registry = load_agent_registry()

    def _get_agent_port(self, agent_name: str, fallback_port: int) -> int:
        """에이전트 이름 기반 환경 변수에서 포트를 가져오고, 없으면 fallback 사용"""
        env_key = f"{agent_name.upper()}_PORT"
        return int(os.getenv(env_key, fallback_port))

    async def fetch_agent_card(self, base_url: str) -> Optional[AgentCard]:
        """에이전트 서버에서 /agent_card 정보를 가져옵니다. 실패 시 재시도합니다."""
        url = f"{base_url}/agent_card"
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    return AgentCard(**data)
            except Exception as e:
                if attempt < RETRY_COUNT:
                    logger.warning(
                        f"🔁 {base_url} 응답 대기 중... 시도 {attempt}/{RETRY_COUNT} (재시도까지 {RETRY_DELAY}초)"
                    )
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"❌ {base_url} 에이전트 카드 요청 실패 (최종 시도): {e}")
                    return None

    async def load_all_cards(self):
        """등록된 모든 에이전트의 카드를 병렬로 로딩합니다."""
        tasks = []
        for agent in self.registry.agents:
            port = self._get_agent_port(agent.name, agent.port)
            base_url = f"http://{agent.host}:{port}"
            tasks.append(self._load_card_for_agent(agent.name, base_url))
        await asyncio.gather(*tasks)

    async def _load_card_for_agent(self, name: str, base_url: str):
        card = await self.fetch_agent_card(base_url)
        if card:
            for skill in card.skills:
                self.cards.setdefault(skill.id, []).append(card)
            logger.info(f"✅ {name} 에이전트 카드 로드 완료")
        else:
            logger.warning(f"⚠️ {name} 에이전트 카드 로드 실패 또는 응답 없음")

    def get_cards_for_action(self, action: str) -> List[AgentCard]:
        if action not in self.cards or not self.cards[action]:
            raise ValueError(f"등록된 에이전트 중 해당 action을 처리할 수 있는 항목이 없습니다: {action}")
        return self.cards[action]

    def get_card_by_name(self, name: str) -> AgentCard:
        for card in self.cards:
            if card.name == name:
                return card
        raise ValueError(f"🔍 AgentCard '{name}'를 찾을 수 없습니다.")

    def get_first_card_for_action(self, action: str) -> AgentCard:
        return self.get_cards_for_action(action)[0]

    def get_random_card_for_action(self, action: str) -> AgentCard:
        return random.choice(self.get_cards_for_action(action))
