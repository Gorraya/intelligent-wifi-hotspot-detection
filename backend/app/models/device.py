"""
Device model - represents a unique IP/MAC observed on the network.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Float, Integer, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), index=True, nullable=False)
    mac_address: Mapped[str | None] = mapped_column(String(17), index=True, nullable=True)
    
    # Current status
    current_label: Mapped[str] = mapped_column(String(20), default="normal")  # normal | hotspot | suspicious
    last_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    total_detections: Mapped[int] = mapped_column(Integer, default=0)
    hotspot_count: Mapped[int] = mapped_column(Integer, default=0)
    
    is_whitelisted: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    events = relationship("DetectionEvent", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
