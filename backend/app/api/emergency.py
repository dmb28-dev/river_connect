from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import EmergencyRequest, EmergencyStatus, User, UserRole
from app.schemas import EmergencyRequestCreate, EmergencyRequestResponse, EmergencyRequestUpdate, MessageResponse
from app.services.deps import get_crew_user, get_current_user, get_passenger_user, ws_authenticate
from app.services.redis_service import publish_event
from app.websockets.manager import emergency_manager

router = APIRouter(prefix="/emergency", tags=["emergency"])


def _to_response(req: EmergencyRequest) -> EmergencyRequestResponse:
    passenger = req.passenger
    return EmergencyRequestResponse(
        id=req.id,
        passenger_id=req.passenger_id,
        vessel_id=req.vessel_id,
        location=req.location,
        status=req.status,
        created_at=req.created_at,
        resolved_at=req.resolved_at,
        assigned_to=req.assigned_to,
        notes=req.notes,
        passenger_name=passenger.full_name if passenger else None,
        passenger_cabin=passenger.cabin_number if passenger else None,
        passenger_phone=passenger.phone if passenger else None,
    )


@router.post("", response_model=EmergencyRequestResponse, status_code=201)
async def create_emergency_request(
    data: EmergencyRequestCreate,
    db: AsyncSession = Depends(get_db),
    passenger: User = Depends(get_passenger_user),
) -> EmergencyRequestResponse:
    if not passenger.vessel_id:
        raise HTTPException(status_code=400, detail="Passenger not assigned to a vessel")

    location = data.location
    if passenger.cabin_number and passenger.cabin_number not in location:
        location = f"{location} (Каюта {passenger.cabin_number})"

    request = EmergencyRequest(
        passenger_id=passenger.id,
        vessel_id=passenger.vessel_id,
        location=location,
        status=EmergencyStatus.pending,
        notes=data.notes,
    )
    db.add(request)
    await db.flush()
    await db.refresh(request, ["passenger"])

    response = _to_response(request)
    event = {"type": "sos_alert", "data": response.model_dump(mode="json")}
    await emergency_manager.broadcast("emergency", event)
    await publish_event("emergency", event)
    return response


@router.get("", response_model=list[EmergencyRequestResponse])
async def list_emergency_requests(
    status_filter: EmergencyStatus | None = None,
    db: AsyncSession = Depends(get_db),
    crew: User = Depends(get_crew_user),
) -> list[EmergencyRequestResponse]:
    query = select(EmergencyRequest).options(selectinload(EmergencyRequest.passenger))
    if crew.vessel_id:
        query = query.where(EmergencyRequest.vessel_id == crew.vessel_id)
    if status_filter:
        query = query.where(EmergencyRequest.status == status_filter)
    query = query.order_by(EmergencyRequest.created_at.desc())

    result = await db.execute(query)
    return [_to_response(r) for r in result.scalars().all()]


@router.patch("/{request_id}/status", response_model=EmergencyRequestResponse)
async def update_emergency_status(
    request_id: int,
    data: EmergencyRequestUpdate,
    db: AsyncSession = Depends(get_db),
    crew: User = Depends(get_crew_user),
) -> EmergencyRequestResponse:
    result = await db.execute(
        select(EmergencyRequest)
        .options(selectinload(EmergencyRequest.passenger))
        .where(EmergencyRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Emergency request not found")

    request.status = data.status
    request.assigned_to = crew.id
    if data.notes:
        request.notes = data.notes
    if data.status == EmergencyStatus.resolved:
        request.resolved_at = datetime.now(timezone.utc)

    response = _to_response(request)
    event = {"type": "sos_update", "data": response.model_dump(mode="json")}
    await emergency_manager.broadcast("emergency", event)
    await publish_event("emergency", event)
    return response


async def emergency_websocket(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    auth = ws_authenticate(token)
    if not auth:
        await websocket.close(code=4001)
        return

    if auth["role"] != UserRole.crew.value and auth["role"] != UserRole.passenger.value:
        await websocket.close(code=4003)
        return

    await emergency_manager.connect("emergency", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        emergency_manager.disconnect("emergency", websocket)
