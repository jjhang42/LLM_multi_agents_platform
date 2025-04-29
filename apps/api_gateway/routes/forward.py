from fastapi import APIRouter, Request
import httpx

router = APIRouter()

@router.post("/")
async def natural_input_forward(request: Request):
    user_input = await request.json()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://orchestrator:8000/",
            json=user_input
        )

    return response.json()
