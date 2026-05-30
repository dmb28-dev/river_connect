from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Notification, NotificationPriority, NotificationRead, NotificationType, User
from app.schemas import (
    EmergencyNotificationCreate,
    MessageResponse,
    NotificationCreate,
    NotificationResponse,
)
from app.services.deps import get_crew_user, get_current_user, ws_authenticate
from app.services.redis_service import publish_event
from app.services.vessel_service import ensure_crew_vessel_access, get_vessel_or_404
from app.websockets.manager import notification_manager

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _to_response(notification: Notification, user_id: int, read_ids: set[int]) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        vessel_id=notification.vessel_id,
        sender_id=notification.sender_id,
        title=notification.title,
        content=notification.content,
        type=notification.type,
        priority=notification.priority,
        created_at=notification.created_at,
        scheduled_at=notification.scheduled_at,
        requires_acknowledgment=notification.requires_acknowledgment,
        is_read=notification.id in read_ids,
    )


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    notification_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    query = select(Notification).options(selectinload(Notification.reads))
    if user.vessel_id:
        query = query.where(Notification.vessel_id == user.vessel_id)
    if notification_type:
        query = query.where(Notification.type == notification_type)
    query = query.order_by(Notification.created_at.desc())

    result = await db.execute(query)
    notifications = result.scalars().all()

    read_result = await db.execute(
        select(NotificationRead.notification_id).where(NotificationRead.user_id == user.id)
    )
    read_ids = set(read_result.scalars().all())

    return [_to_response(n, user.id, read_ids) for n in notifications]


@router.post("", response_model=NotificationResponse, status_code=201)
async def create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    crew: User = Depends(get_crew_user),
) -> NotificationResponse:
    await get_vessel_or_404(db, data.vessel_id)
    await ensure_crew_vessel_access(crew, data.vessel_id)

    notification = Notification(
        vessel_id=data.vessel_id,
        sender_id=crew.id,
        title=data.title,
        content=data.content,
        type=data.type,
        priority=data.priority,
        scheduled_at=data.scheduled_at,
        requires_acknowledgment=data.requires_acknowledgment,
    )
    db.add(notification)
    await db.flush()

    payload = _to_response(notification, crew.id, set())
    await notification_manager.broadcast("notifications", {"type": "new_notification", "data": payload.model_dump(mode="json")})
    await publish_event("notifications", {"type": "new_notification", "data": payload.model_dump(mode="json")})
    return payload


@router.post("/emergency", response_model=NotificationResponse, status_code=201)
async def create_emergency_notification(
    data: EmergencyNotificationCreate,
    db: AsyncSession = Depends(get_db),
    crew: User = Depends(get_crew_user),
) -> NotificationResponse:
    await get_vessel_or_404(db, data.vessel_id)
    await ensure_crew_vessel_access(crew, data.vessel_id)

    content = data.content
    if data.instructions:
        content = f"{content}\n\nИнструкции: {data.instructions}"

    notification = Notification(
        vessel_id=data.vessel_id,
        sender_id=crew.id,
        title=data.title,
        content=content,
        type=NotificationType.emergency,
        priority=data.priority,
        requires_acknowledgment=True,
    )
    db.add(notification)
    await db.flush()

    payload = _to_response(notification, crew.id, set())
    event = {"type": "emergency_alert", "data": payload.model_dump(mode="json")}
    await notification_manager.broadcast("notifications", event)
    await publish_event("notifications", event)
    return payload


@router.patch("/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageResponse:
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    existing = await db.execute(
        select(NotificationRead).where(
            NotificationRead.notification_id == notification_id,
            NotificationRead.user_id == user.id,
        )
    )
    if not existing.scalar_one_or_none():
        db.add(NotificationRead(notification_id=notification_id, user_id=user.id, read_at=datetime.now(timezone.utc)))

    return MessageResponse(message="Marked as read")


async def notifications_websocket(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    auth = ws_authenticate(token)
    if not auth:
        await websocket.close(code=4001)
        return

    await notification_manager.connect("notifications", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_manager.disconnect("notifications", websocket)
