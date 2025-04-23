import yaml
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel
from core.system.config import settings

class AgentEntry(BaseModel):
    name: str
    host: str
    port: int
    endpoint: str

class AgentRegistry(BaseModel):
    agents: List[AgentEntry]

    def get_agent_url(self, name: str) -> Optional[str]:
        agent = next((a for a in self.agents if a.name == name), None)
        if agent:
            return f"http://{agent.host}:{agent.port}{agent.endpoint}"
        return None

def load_agent_registry(path: Optional[str] = None) -> AgentRegistry:
    registry_path = Path(path or settings.AGENT_REGISTRY_PATH)
    if not registry_path.exists():
        raise FileNotFoundError(f"Agent registry file not found: {registry_path}")
    
    with open(registry_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return AgentRegistry(**data)

def get_agent_url_from_registry(name: str) -> str:
    registry = load_agent_registry()
    url = registry.get_agent_url(name)
    if not url:
        raise ValueError(f"Agent '{name}' not found in registry.")
    return url
