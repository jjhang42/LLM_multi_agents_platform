# /core/system/utils/agent_card_utils.py

from typing import Dict, List, Union
from core.system.formats.agent_card import AgentCard

def group_cards_by_action(cards: List[Union[AgentCard, dict]]) -> Dict[str, List[AgentCard]]:
    """
    에이전트 카드 리스트를 받아 action_id별로 그룹핑합니다.
    dict 타입이 들어오면 AgentCard로 역직렬화합니다.
    """
    grouped: Dict[str, List[AgentCard]] = {}

    for card in cards:
        # dict일 경우 AgentCard로 변환
        if isinstance(card, dict):
            card = AgentCard(**card)

        for skill in card.skills:
            grouped.setdefault(skill.id, []).append(card)

    return grouped
