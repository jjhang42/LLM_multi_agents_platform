from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict


class AgentProvider(BaseModel):
    organization: str
    url: HttpUrl


class AgentCapabilities(BaseModel):
    streaming: Optional[bool] = False
    pushNotifications: Optional[bool] = False
    stateTransitionHistory: Optional[bool] = False


class AgentAuthentication(BaseModel):
    schemes: List[str]  # e.g. ["Bearer", "Basic"]
    credentials: Optional[str] = None  # Token or secret if needed


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]
    examples: Optional[List[str]] = None
    inputModes: Optional[List[str]] = None   # MIME types
    outputModes: Optional[List[str]] = None


class AgentCard(BaseModel):
    name: str  # Human-readable name
    description: str
    url: HttpUrl
    provider: Optional[AgentProvider] = None
    version: str  # e.g. "1.0.0"
    documentationUrl: Optional[HttpUrl] = None
    capabilities: AgentCapabilities
    authentication: AgentAuthentication
    defaultInputModes: List[str]   # e.g. ["text/plain", "application/json"]
    defaultOutputModes: List[str]
    skills: List[AgentSkill]
