from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BROKER_TYPE: str = "http"
    BROKER_PROTOCOL: str = "http"
    BROKER_HTTP_HOST: str = "broker"
    BROKER_HTTP_PORT: int = 8000
    AGENT_REGISTRY_PATH: str = "core/system/agent_registry.yaml"

    FRONTEND_PORT: int = 3000
    ORCHESTRATOR_PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()

def get_broker_url(endpoint: str) -> str:
    protocol = settings.BROKER_PROTOCOL or "http"
    return f"{protocol}://{settings.BROKER_HTTP_HOST}:{settings.BROKER_HTTP_PORT}/{endpoint}"

def get_agent_url(agent_name: str, endpoint: str) -> str:
    raise NotImplementedError("agent_registry.yaml 기반의 URL 조회는 별도 로더에서 처리합니다.")
