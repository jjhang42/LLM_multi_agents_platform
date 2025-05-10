from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 각 라우터를 파일별로 명시적으로 import
from apps.api_gateway.routes.graph import router as graph_router
from apps.api_gateway.routes.task import router as task_router
from apps.api_gateway.routes.tasks import router as tasks_router

app = FastAPI(title="LLM API Gateway")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(graph_router)
app.include_router(task_router)
app.include_router(tasks_router)
# 헬스 체크
@app.get("/health")
async def health_check():
    return {"status": "api_gateway running"}
