"""
Devices API.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.device import Device
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class DeviceOut(BaseModel):
    id: int
    ip_address: str
    mac_address: Optional[str]
    current_label: str
    last_confidence: float
    first_seen: datetime
    last_seen: datetime
    total_detections: int
    hotspot_count: int
    is_whitelisted: bool
    notes: Optional[str]

    class Config:
        from_attributes = True


class DeviceUpdate(BaseModel):
    is_whitelisted: Optional[bool] = None
    notes: Optional[str] = None


@router.get("/", response_model=List[DeviceOut])
async def list_devices(
    label: Optional[str] = Query(None, description="Filter by label: normal | hotspot"),
    search: Optional[str] = Query(None, description="Search IP or MAC"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Device).order_by(desc(Device.last_seen)).limit(limit)

    if label:
        query = query.where(Device.current_label == label)
    if search:
        query = query.where(
            (Device.ip_address.ilike(f"%{search}%")) |
            (Device.mac_address.ilike(f"%{search}%"))
        )

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{device_id}", response_model=DeviceOut)
async def get_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.patch("/{device_id}", response_model=DeviceOut)
async def update_device(
    device_id: int,
    payload: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if payload.is_whitelisted is not None:
        device.is_whitelisted = payload.is_whitelisted
    if payload.notes is not None:
        device.notes = payload.notes

    await db.commit()
    await db.refresh(device)
    return device
