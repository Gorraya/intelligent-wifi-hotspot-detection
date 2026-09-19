"""
Pydantic schemas for Detection Events.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, IPvAnyAddress


class EventIngest(BaseModel):
    """Schema used by Detection Agent to send results."""
    ip_address: str
    mac_address: Optional[str] = None
    label: str = Field(..., pattern="^(normal|hotspot)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    features: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class EventOut(BaseModel):
    id: int
    device_id: int
    label: str
    confidence: float
    features: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
