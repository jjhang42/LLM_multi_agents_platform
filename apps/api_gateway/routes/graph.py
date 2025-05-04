# apps/api_gateway/routes/graph.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

# 예시 모델 (실제 프로젝트에서는 Pydantic 모델로 정식화해야 함)
class TaskNode(BaseModel):
    id: str
    label: str
    status: str
    depends_on: List[str] = []

# 가상 그래프 데이터 (실제 로직은 orchestrator 등에서 받아야 함)
mock_graph_data = {
    "task-abc": [
        {"id": "t1", "label": "Parse", "status": "done"},
        {"id": "t2", "label": "Execute", "status": "pending", "depends_on": ["t1"]},
    ]
}

@router.get("/api/tasks/{task_id}/graph", response_model=List[TaskNode])
async def get_task_graph(task_id: str):
    return mock_graph_data.get(task_id, [])
