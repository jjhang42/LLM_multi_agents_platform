import httpx
from typing import List, Dict

async def fetch_agent_cards() -> List[Dict]:
    """
    브로커로부터 에이전트 카드 목록을 가져옵니다.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://broker:8000/agents")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"❌ [Orchestrator] agent 카드 로드 실패: {e}")
        return []
