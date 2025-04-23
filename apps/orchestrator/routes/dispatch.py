from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from core.system.formats.a2a_task import TaskSendParams
from apps.orchestrator.services.task_dispatcher import dispatch_task
import traceback

router = APIRouter()

@router.post("/dispatch")
async def dispatch_task_endpoint(task_data: TaskSendParams):
    try:
        result = await dispatch_task(task_data)
        return result
    except Exception as e:
        traceback.print_exc()  # ✅ 콘솔에 전체 예외 출력
        raise HTTPException(status_code=500, detail=str(e))
