"""
Analytics API for Dashboard summary cards and charts.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.device import Device
from app.models.event import DetectionEvent
from app.models.alert import Alert
from app.models.user import User
from app.api.v1.auth import get_current_user

router = APIRouter()


class SummaryStats(BaseModel):
    total_devices: int
    hotspot_devices: int
    normal_devices: int
    total_alerts: int
    unacknowledged_alerts: int
    detections_last_24h: int


class TimelinePoint(BaseModel):
    hour: str
    normal: int
    hotspot: int


@router.get("/summary", response_model=SummaryStats)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_devices = (await db.execute(select(func.count(Device.id)))).scalar() or 0
    hotspot_devices = (await db.execute(
        select(func.count(Device.id)).where(Device.current_label == "hotspot")
    )).scalar() or 0
    normal_devices = total_devices - hotspot_devices

    total_alerts = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    unacknowledged = (await db.execute(
        select(func.count(Alert.id)).where(Alert.is_acknowledged == False)
    )).scalar() or 0

    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    detections_24h = (await db.execute(
        select(func.count(DetectionEvent.id)).where(DetectionEvent.created_at >= last_24h)
    )).scalar() or 0

    return SummaryStats(
        total_devices=total_devices,
        hotspot_devices=hotspot_devices,
        normal_devices=normal_devices,
        total_alerts=total_alerts,
        unacknowledged_alerts=unacknowledged,
        detections_last_24h=detections_24h,
    )


@router.get("/timeline", response_model=List[TimelinePoint])
async def get_timeline(
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simple hourly timeline of normal vs hotspot detections."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    result = await db.execute(
        select(DetectionEvent).where(DetectionEvent.created_at >= since)
    )
    events = result.scalars().all()

    buckets = {}
    for e in events:
        key = e.created_at.strftime("%Y-%m-%d %H:00")
        if key not in buckets:
            buckets[key] = {"normal": 0, "hotspot": 0}
        if e.label == "hotspot":
            buckets[key]["hotspot"] += 1
        else:
            buckets[key]["normal"] += 1

    timeline = [
        TimelinePoint(hour=k, normal=v["normal"], hotspot=v["hotspot"])
        for k, v in sorted(buckets.items())
    ]
    return timeline
