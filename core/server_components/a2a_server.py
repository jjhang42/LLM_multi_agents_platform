from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from core.system.formats.a2a import (
    SendTaskRequest,
    SendTaskStreamingRequest,
    SendTaskResponse,
    SendTaskStreamingResponse,
    JSONRPCResponse,
    AgentCard,
)

logger = logging.getLogger(__name__)

class A2AServer:
    def __init__(self, agent_card: AgentCard, task_manager, host: str = "0.0.0.0", port: int = 8000):
        self.agent_card = agent_card
        self.task_manager = task_manager
        self.host = host
        self.port = port
        self.app = FastAPI()
        self._setup_routes()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        @self.app.post("/task", response_model=SendTaskResponse)
        async def handle_task(request: Request):
            body = await request.json()
            try:
                task_request = SendTaskRequest(**body)
                logger.info(f"📩 Received task: {task_request.id}")
                return await self.task_manager.on_send_task(task_request)
            except Exception as e:
                logger.exception("❌ Failed to process task")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.post("/task/subscribe", response_model=SendTaskStreamingResponse)
        async def handle_task_subscribe(request: Request):
            body = await request.json()
            try:
                subscribe_request = SendTaskStreamingRequest(**body)
                return await self.task_manager.on_send_task_subscribe(subscribe_request)
            except Exception as e:
                logger.exception("❌ Subscription failed")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.get("/agent_card", response_model=AgentCard)
        async def get_agent_card():
            return self.agent_card

        @self.app.get("/health")
        async def health():
            return {"status": "ok", "service": self.agent_card.name}

    def start(self):
        uvicorn.run(self.app, host=self.host, port=self.port)
