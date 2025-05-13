# agent_creator/routes/endpoints.py

import time
from fastapi import APIRouter
from core.server_components.a2a_server import A2AServer
from core.system.formats.agent_card import AgentCard

def register_routes(server: A2AServer, agent_card: AgentCard, start_time: float):
    """
    공통 라우트 등록 함수
    - /health
    - /agent_card
    """
    router = APIRouter()

    @router.get("/health")
    def health_check():
        return {
            "status": "ok",
            "service": agent_card.name,
            "version": agent_card.version,
            "uptime": f"{time.time() - start_time:.2f}s"
        }

    @router.get("/agent_card", response_model=AgentCard)
    def get_agent_card():
        return agent_card

    server.app.include_router(router)
