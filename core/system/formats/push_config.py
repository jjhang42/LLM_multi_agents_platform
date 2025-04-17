from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List


class PushAuthentication(BaseModel):
    schemes: List[str]
    credentials: Optional[str] = None
  

class PushNotificationConfig(BaseModel):
    url: HttpUrl
    token: Optional[str] = None
    authentication: Optional[PushAuthentication] = None


class TaskPushNotificationConfig(BaseModel):
    id: str  # Task ID
    pushNotificationConfig: PushNotificationConfig
