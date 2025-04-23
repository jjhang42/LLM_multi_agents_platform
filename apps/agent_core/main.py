# apps/agent_core/main.py
from fastapi import FastAPI
from core.system.formats.a2a_task import Task
from core.system.formats.trace_log import TraceLog
from fastapi.responses import JSONResponse
import traceback
import time
import os

app = FastAPI()
AGENT_NAME = "agent_core"

@app.get("/")
def root():
    return {"message": f"{AGENT_NAME} is alive"}

@app.get("/health")
def health_check():
    start_time = float(os.getenv("START_TIME", str(time.time())))
    return {
        "status": "ok",
        "service": AGENT_NAME,
        "version": "1.0.0",
        "uptime": f"{time.time() - start_time:.2f}s"
    }

@app.post("/task")
async def handle_task(task: Task):
    start_time = time.time()
    try:
        print(f"\n[{AGENT_NAME}] Task Received:")
        print(f" ├─ ID         : {task.id}")
        print(f" ├─ Session ID : {task.session_id}")
        print(f" ├─ State      : {task.status.state}")
        print(f" ├─ Message    : {task.status.message.parts[0].text}")
        print(f" └─ Metadata   : {task.metadata}")
        
        # agent_core 고유 처리 로직
        result = {
            "status": "done",
            "task_id": task.id,
            "message": f"[{AGENT_NAME}] processed: {task.status.message.parts[0].text}",
            "processing_time": f"{time.time() - start_time:.2f}s"
        }
        
        print(f"[{AGENT_NAME}] Task Processed: {task.id}")
        print(f" └─ Response: {result}")
        
        return JSONResponse(content=result)
    except Exception as e:
        print(f"\n[{AGENT_NAME}] Error Processing Task:")
        print(f" ├─ Task ID: {task.id}")
        print(f" ├─ Error: {str(e)}")
        print(f" └─ Stack Trace:")
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "task_id": task.id,
                "processing_time": f"{time.time() - start_time:.2f}s"
            }
        )

@app.post("/trace")
async def handle_trace(trace: TraceLog):
    print(f"[{AGENT_NAME}][TraceLog] {trace.event_type} | task={trace.task_id}")
    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    os.environ["START_TIME"] = str(time.time())
    uvicorn.run(app, host="0.0.0.0", port=8000)