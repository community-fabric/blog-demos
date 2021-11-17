from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Snapshot(BaseModel):
    id: str
    name: Optional[str]


class Event(BaseModel):
    type: str
    action: str
    status: str
    test: Optional[bool] = False
    requester: str
    snapshot: Optional[Snapshot] = None
    timestamp: datetime
