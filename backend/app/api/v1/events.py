"""
Events API - receives detection results from the Agent.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models.device import Device
from app.models.event import DetectionEvent
from app.models.alert import Alert
from app.schemas.event import EventIngest

router = APIRouter()


@router.post("/ingest", response_model=dict, status_code=status.HTTP_201_CREATED)
async def ingest_event(payload: EventIngest, db: AsyncSession = Depends(get_db)):
    """
    Endpoint used by the Detection Agent to push classification results.
    """
    # Find or create device
    result = await db.execute(
        select(Device).where(Device.ip_address == payload.ip_address)
    )
    device = result.scalar_one_or_none()

    if not device:
        device = Device(
            ip_address=payload.ip_address,
            mac_address=payload.mac_address,
            current_label=payload.label,
            last_confidence=payload.confidence,
        )
        db.add(device)
        await db.flush()
    else:
        device.current_label = payload.label
        device.last_confidence = payload.confidence
        device.last_seen = datetime.now(timezone.utc)
        device.total_detections += 1
        if payload.label == "hotspot":
            device.hotspot_count += 1

    # Create detection event
    event = DetectionEvent(
        device_id=device.id,
        label=payload.label,
        confidence=payload.confidence,
        features=payload.features,
    )
    db.add(event)
    await db.flush()

    # 1 device = 1 alert (create or update)
    if payload.label == "hotspot" and payload.confidence >= 0.55 and not device.is_whitelisted:
        existing = await db.execute(
            select(Alert).where(
                Alert.device_id == device.id,
                Alert.is_acknowledged == False,
            )
        )
        alert = existing.scalar_one_or_none()

        if alert:
            alert.event_id = event.id
            alert.confidence = payload.confidence
            alert.severity = "high" if payload.confidence >= 0.85 else "medium"
            alert.title = f"Hotspot Detected: {payload.ip_address}"
            alert.message = (
                f"Device {payload.ip_address} classified as hotspot "
                f"with {payload.confidence:.1%} confidence."
            )
        else:
            alert = Alert(
                device_id=device.id,
                event_id=event.id,
                severity="high" if payload.confidence >= 0.85 else "medium",
                title=f"Hotspot Detected: {payload.ip_address}",
                message=(
                    f"Device {payload.ip_address} classified as hotspot "
                    f"with {payload.confidence:.1%} confidence."
                ),
                confidence=payload.confidence,
            )
            db.add(alert)

    await db.commit()

    return {
        "status": "ok",
        "device_id": device.id,
        "event_id": event.id,
        "label": payload.label,
    }