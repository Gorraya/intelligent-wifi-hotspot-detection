"""
DetectionEvent model - stores every classification result from the Agent.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    
    label: Mapped[str] = mapped_column(String(20), nullable=False)  # normal | hotspot
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    
    features: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    device = relationship("Device", back_populates="events")
