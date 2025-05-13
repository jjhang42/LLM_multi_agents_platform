from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from broker.routes.tasks import router as tasks_router
from broker.routes.agents import router as agents_router
from broker.routes.health import router as health_router
from broker.core.agent_card_loader import AgentCardLoader
from broker.core.executor_runner import ExecutorRunner
from core.system.memory.agent_card_store import AgentCardStore

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 카드로더
card_loader = AgentCardLoader()

@app.on_event("startup")
async def on_startup():
    await card_loader.load_all_cards()
    runner = ExecutorRunner(card_loader)
    AgentCardStore.save(card_loader.cards)

    app.state.runner = runner
    print("✅ [Broker] Agent cards loaded and executor runner initialized.")

app.include_router(tasks_router)
app.include_router(agents_router)
app.include_router(health_router)
