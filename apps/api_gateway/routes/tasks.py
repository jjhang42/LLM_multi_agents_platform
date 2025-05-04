# apps/api_gateway/routes/tasks.py
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class Task(BaseModel):
    id: str
    status: str
    message: str
    created_at: datetime

@router.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    # TODO:
    return Task(
        id=task_id,
        status="in_progress",
        message="처리 중입니다.",
        created_at=datetime.utcnow()
    )
