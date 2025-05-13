from typing import Dict, List

class SessionMessageMemory:
    """
    context_id 단위의 대화 메시지 기억 모듈 (사용자 ↔ 어시스턴트 메시지)
    """
    _messages: Dict[str, List[Dict[str, str]]] = {}

    @classmethod
    def append(cls, context_id: str, role: str, text: str):
        cls._messages.setdefault(context_id, []).append({
            "role": role,
            "text": text
        })
        print(f"💬 [SessionMessageMemory] {role} 메시지 저장됨 → context: {context_id}")

    @classmethod
    def get(cls, context_id: str) -> List[Dict[str, str]]:
        return cls._messages.get(context_id, [])

    @classmethod
    def clear(cls, context_id: str):
        cls._messages.pop(context_id, None)
        print(f"🧹 [SessionMessageMemory] context {context_id} 기록 초기화됨")
