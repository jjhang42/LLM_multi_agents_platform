from fastapi import FastAPI
import uvicorn
import httpx
from core.system.config import settings
from core.system.agent_registry import load_agent_registry

from core.system.formats.a2a_task import Task
from core.system.formats.trace_log import TraceLog
from apps.broker.core.router import route_task

app = FastAPI()

@app.get("/")
def root():
    return {"message": "📦 Broker is alive"}

@app.get("/health")
async def health_check():
    # 에이전트 레지스트리 확인
    registry_status = "unknown"
    try:
        registry = load_agent_registry()
        registry_status = "ok" if registry.agents else "error: no agents"
    except Exception as e:
        registry_status = f"error: {str(e)}"

    # 에이전트 연결 확인
    agent_statuses = {}
    try:
        registry = load_agent_registry()
        async with httpx.AsyncClient() as client:
            for agent in registry.agents:
                try:
                    response = await client.get(f"http://{agent.host}:{agent.port}/health", timeout=5.0)
                    agent_statuses[agent.name] = "ok" if response.status_code == 200 else "error"
                except Exception as e:
                    agent_statuses[agent.name] = f"error: {str(e)}"
    except Exception as e:
        agent_statuses["error"] = str(e)

    return {
        "status": "ok",
        "service": "broker",
        "dependencies": {
            "registry": registry_status,
            "agents": agent_statuses
        }
    }

@app.post("/task")
async def receive_task(task: Task):
    print(f"\n📦 [Broker] Received Task")
    print(f" ├─ ID         : {task.id}")
    print(f" ├─ Session ID : {task.session_id}")
    print(f" ├─ State      : {task.status.state}")
    print(f" └─ Metadata   : {task.metadata}")
    return await route_task(task)

@app.post("/trace")
async def receive_trace(trace: TraceLog):
    print(f"\n[TraceLog] Event: {trace.event_type}")
    print(f" ├─ Task ID    : {trace.task_id}")
    print(f" ├─ Session ID : {trace.session_id}")
    print(f" ├─ Source     : {trace.source} → {trace.target}")
    print(f" └─ Payload    : {trace.payload}")
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
