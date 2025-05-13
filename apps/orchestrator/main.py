from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from apps.orchestrator.services.parser_router import parse_and_dispatch_task
from apps.orchestrator.utils.error import handle_exception
from core.system.formats.a2a_part import Part

class TaskRequest(BaseModel):
    task_id: str
    parts: List[Part]

def create_app() -> FastAPI:
    app = FastAPI()

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Task 요청 엔드포인트
    @app.post("/")
    @app.post("/task")
    async def handle_task(request: Request):
        try:
            body = await request.json()
            task_req = TaskRequest(**body)
            return await parse_and_dispatch_task(task_req)
        except Exception as e:
            return handle_exception("request", e)

    # 헬스 체크 엔드포인트
    @app.get("/health")
    async def health():
        return {"status": "orchestrator alive"}

    return app

app = create_app()
