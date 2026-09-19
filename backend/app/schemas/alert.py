"""
Alert related schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    device_id: int
    event_id: Optional[int] = None
    severity: str
    title: str
    message: Optional[str] = None
    confidence: float
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
