"""
Device related schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DeviceOut(BaseModel):
    id: int
    ip_address: str
    mac_address: Optional[str] = None
    current_label: str
    last_confidence: float
    first_seen: datetime
    last_seen: datetime
    total_detections: int
    hotspot_count: int
    is_whitelisted: bool
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class DeviceUpdate(BaseModel):
    is_whitelisted: Optional[bool] = None
    notes: Optional[str] = None
