from typing import Dict, List
from core.system.formats.agent_card import AgentCard

class AgentCardStore:
    """
    브로커 또는 시스템에서 로딩한 AgentCard들을 메모리에 저장/조회합니다.
    """

    _cards: Dict[str, List[AgentCard]] = {}

    @classmethod
    def save(cls, cards: Dict[str, List[AgentCard]]):
        """
        에이전트 카드들을 저장합니다. 일반적으로 card_loader.cards 전체를 넣습니다.
        """
        cls._cards = cards
        print(f"🧠 [AgentCardStore] {sum(len(v) for v in cards.values())}개 카드 저장됨")

    @classmethod
    def get(cls) -> Dict[str, List[AgentCard]]:
        """
        전체 카드 딕셔너리 반환: {action_id: [AgentCard, ...]}
        """
        return cls._cards

    @classmethod
    def get_all(cls) -> List[AgentCard]:
        """
        모든 AgentCard 객체들을 하나의 리스트로 평탄화하여 반환
        """
        return [card for cards in cls._cards.values() for card in cards]

    @classmethod
    def get_by_action(cls, action: str) -> List[AgentCard]:
        """
        특정 action에 대응 가능한 에이전트 카드 리스트 반환
        """
        return cls._cards.get(action, [])

    @classmethod
    def list_actions(cls) -> List[str]:
        """
        현재 등록된 action 종류 목록
        """
        return list(cls._cards.keys())
