from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class PushAuthentication(BaseModel):
    schemes: List[str]
    credentials: Optional[str] = None


class PushNotificationConfig(BaseModel):
    url: HttpUrl
    token: Optional[str] = None
    authentication: Optional[PushAuthentication] = None


class TaskPushNotificationConfig(BaseModel):
    id: str
    push_notification_config: PushNotificationConfig
