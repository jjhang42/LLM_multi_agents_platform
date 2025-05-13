from .agents import router as agents_router
from .tasks import router as tasks_router
from .health import router as health_router

routers = [agents_router, tasks_router, health_router]
