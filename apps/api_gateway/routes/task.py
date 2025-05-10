from fastapi import APIRouter, Request, HTTPException
from starlette.responses import JSONResponse
import httpx
from pydantic import BaseModel
from typing import List, Union, Optional

class ImagePart(BaseModel):
    type: str
    data_url: str
    name: str

class TextPart(BaseModel):
    type: str
    text: str

class TaskRequest(BaseModel):
    task_id: str
    parts: List[Union[ImagePart, TextPart]]

router = APIRouter()

@router.post("/task")
async def forward_task(request: Request):
    try:
        payload = await request.json()
        
        # ✅ 수신한 payload 전체 출력
        print("payload:", payload)

        # 데이터 검증
        task_request = TaskRequest(**payload)

        # ✅ 각 필드 출력
        # print("task_id:", task_request.task_id)
        # print("parts:", task_request.parts)

        # parts 배열이 비어있는지 확인
        if not task_request.parts:
            raise HTTPException(status_code=400, detail="parts array cannot be empty")
            
        # 각 part의 type이 올바른지 확인
        for part in task_request.parts:
            print("part 내용:", part)
            if part.type not in ["text", "image"]:
                raise HTTPException(status_code=400, detail=f"Invalid part type: {part.type}")
            if part.type == "text" and not part.text:
                raise HTTPException(status_code=400, detail="Text part cannot be empty")
            if part.type == "image" and not part.data_url:
                raise HTTPException(status_code=400, detail="Image part must have data_url")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://orchestrator:8000/task",
                json=task_request.dict()
            )

        if response.status_code == 200:
            return JSONResponse(status_code=200, content=response.json())

        else:
            return JSONResponse(status_code=502, content={"error": "Orchestrator error", "detail": response.text})

    except HTTPException as e:
        print("HTTPException:", str(e.detail))
        return JSONResponse(status_code=e.status_code, content={"error": str(e.detail)})
    except Exception as e:
        print("Nomal Error:", str(e))
        return JSONResponse(status_code=400, content={"error": "Request forwarding failed", "detail": str(e)})
