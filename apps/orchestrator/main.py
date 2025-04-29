from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.adapters.planner.planner_router import get_planner
from core.system.parser.task_assembler import assemble_tasks_with_graph
import uuid
import os
from core.system.debug.task_debugger import debug_print_tasks_and_graph

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["http://127.0.0.1:3000"]처럼 구체적으로 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def natural_language_to_tasks(request: Request):
    print("[DEBUG] Received POST / request in Orchestrator")

    body = await request.json()
    input_text = body.get("message", "")
    print("[DEBUG] Input text:", input_text)

    planner = get_planner()
    print("[DEBUG] Planner selected:", planner.__class__.__name__)

    tasks, graph = await planner.parse(input_text)

    tasks, graph = assemble_tasks_with_graph(tasks)

    # 🧩 공통 context_id 부여
    context_id = str(uuid.uuid4())
    for task in tasks.values():
        task["context_id"] = context_id
    
    debug_print_tasks_and_graph(tasks, graph)

    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post("http://broker:8000/task", json={
            "context_id": context_id,
            "tasks": tasks,
            "graph": graph.serialize()
        })

    return {
        "status": "tasks_generated",
        "context_id": context_id,
        "tasks": tasks,
        "graph": graph.serialize()
    }

@app.get("/health")
async def health():
    return {"status": "orchestrator alive"}

# from fastapi import FastAPI
# from apps.orchestrator.routes import dispatch
# import uvicorn
# import httpx
# from core.system.config import settings

# app = FastAPI()
# app.include_router(dispatch.router, prefix="/api")

# @app.get("/")
# def root():
#     return {"message": "Orchestrator is alive"}

# @app.get("/health")
# async def health_check():
#     # Broker 연결 확인
#     broker_status = "unknown"
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(f"http://{settings.BROKER_HTTP_HOST}:{settings.BROKER_HTTP_PORT}/health")
#             broker_status = "ok" if response.status_code == 200 else "error"
#     except Exception as e:
#         broker_status = f"error: {str(e)}"

#     return {
#         "status": "ok",
#         "service": "orchestrator",
#         "dependencies": {
#             "broker": broker_status
#         }
#     }

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
