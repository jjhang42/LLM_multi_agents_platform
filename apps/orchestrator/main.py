from fastapi import FastAPI
from apps.orchestrator.routes import dispatch
import uvicorn
import httpx
from core.system.config import settings

app = FastAPI()
app.include_router(dispatch.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Orchestrator is alive"}

@app.get("/health")
async def health_check():
    # Broker 연결 확인
    broker_status = "unknown"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{settings.BROKER_HTTP_HOST}:{settings.BROKER_HTTP_PORT}/health")
            broker_status = "ok" if response.status_code == 200 else "error"
    except Exception as e:
        broker_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "service": "orchestrator",
        "dependencies": {
            "broker": broker_status
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
