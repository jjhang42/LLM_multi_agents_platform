# apps/api_gateway/routes/messages.py
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
import asyncio

router = APIRouter()

# 🧾 메시지 모델
class Message(BaseModel):
    sender: str
    content: str
    timestamp: datetime

# 🧠 임시 메모리 저장소 (실제 구현 시 Redis 또는 DB 사용)
task_messages = {}

# ✅ 메시지 전체 조회
@router.get("/api/tasks/{task_id}/messages", response_model=List[Message])
async def get_messages(task_id: str):
    return task_messages.get(task_id, [])

# ✅ 메시지 추가
@router.post("/api/tasks/{task_id}/messages", response_model=Message)
async def add_message(task_id: str, msg: Message):
    task_messages.setdefault(task_id, []).append(msg)
    return msg

# ✅ SSE 스트리밍
@router.get("/api/tasks/{task_id}/messages/stream")
async def message_stream(task_id: str, request: Request):
    async def event_generator():
        last_index = 0
        while True:
            if await request.is_disconnected():
                break
            messages = task_messages.get(task_id, [])
            if len(messages) > last_index:
                for msg in messages[last_index:]:
                    yield f"data: {msg.json()}\n\n"
                last_index = len(messages)
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
