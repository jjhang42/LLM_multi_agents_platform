from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.adapters.planner.planner_router import get_planner
from core.system.parser.task_input_injector import inject_input_text_to_tasks
from core.system.debug.task_debugger import debug_print_loose_tasks_and_graph
from core.system.utils.serialize import serialize
import uuid
import httpx
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def natural_language_to_tasks(request: Request):
    print("[DEBUG] Received POST / request in Orchestrator")

    # ✅ 사용자 입력 수신
    body = await request.json()
    input_text = body.get("message", "")
    print("[DEBUG] Input text:", input_text)

    # ✅ Planner 선택 및 태스크 생성
    planner = get_planner()
    print("[DEBUG] Planner selected:", planner.__class__.__name__)

    try:
        tasks, graph = await planner.parse(input_text)
        print(f"[DEBUG] Parsed task count: {len(tasks)}")
    except Exception as e:
        traceback.print_exc()
        return {"status": "planner_error", "error": str(e)}

    # ✅ 사용자 입력 메시지 → Task.message 및 metadata 주입
    inject_input_text_to_tasks(tasks, input_text)

    # ✅ context_id 부여
    context_id = str(uuid.uuid4())
    for task in tasks.values():
        if isinstance(task, dict):
            task["context_id"] = context_id
        else:
            task.metadata = task.metadata or {}
            task.metadata["context_id"] = context_id

    # ✅ 디버깅 출력
    debug_print_loose_tasks_and_graph(tasks, graph)

    # ✅ 직렬화 후 Broker로 전송
    payload = serialize({
        "context_id": context_id,
        "tasks": tasks,
        "graph": graph.serialize()
    })

    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post("http://broker:8000/tasks", json=payload)

    return payload

@app.get("/health")
async def health():
    return {"status": "orchestrator alive"}
