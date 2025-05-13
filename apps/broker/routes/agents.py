# apps/broker/routes/agents.py
from fastapi import APIRouter
from core.system.memory.agent_card_store import AgentCardStore

router = APIRouter()

@router.get("/agents")
async def get_agents():
    return [
        card.dict()
        for cards in AgentCardStore.get().values()
        for card in cards
    ]
