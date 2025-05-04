# broker/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.system.formats.a2a import TaskGraphPayload, TaskSendResult
from core.system.metadata.task_graph import TaskGraph

app = FastAPI()

tasks = {}
graph = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/tasks", response_model=TaskSendResult)
async def receive_tasks(payload: TaskGraphPayload):
    global tasks, graph

    # ✅ tasks와 graph 분리 저장
    tasks = payload.tasks
    graph = TaskGraph(dependencies=payload.graph)

    print("[DEBUG] Received tasks:", list(tasks.keys()))
    print("[DEBUG] Received graph dependencies:", graph.dependencies)

    return TaskSendResult(
        status="broker_received",
        context_id=payload.context_id,
        message=f"{len(tasks)} tasks received and registered."
    )

@app.get("/health")
async def health():
    return {"status": "broker alive"}
