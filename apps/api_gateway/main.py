from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api_gateway.routes.forward import router as forward_router
from apps.api_gateway.routes import messages, upload, graph

app = FastAPI(title="LLM API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forward_router)
app.include_router(messages.router)
app.include_router(upload.router)
app.include_router(graph.router)

@app.get("/health")
async def health_check():
    return {"status": "api_gateway running"}
