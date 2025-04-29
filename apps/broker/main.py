from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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

@app.post("/tasks")
async def receive_tasks(request: Request):
    global tasks, graph

    body = await request.json()
    tasks = body.get("tasks", {})
    graph_data = body.get("graph", {})

    # TaskGraph 복원
    graph = TaskGraph.deserialize(graph_data)

    print("[DEBUG] Received tasks:", tasks.keys())
    print("[DEBUG] Received graph dependencies:", graph.dependencies)

    return {"status": "broker_received", "task_count": len(tasks)}

@app.get("/health")
async def health():
    return {"status": "broker alive"}
