from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, get_db
from app.models import Route, User, Vessel, VesselTelemetry
from app.schemas import RouteResponse, TelemetryResponse, VesselResponse
from app.services.deps import get_current_user, ws_authenticate
from app.websockets.manager import vessel_manager

router = APIRouter(prefix="/vessels", tags=["vessels"])


@router.get("", response_model=list[VesselResponse])
async def list_vessels(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Vessel]:
    result = await db.execute(select(Vessel).order_by(Vessel.id))
    return list(result.scalars().all())


@router.get("/{vessel_id}", response_model=VesselResponse)
async def get_vessel(
    vessel_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Vessel:
    result = await db.execute(select(Vessel).where(Vessel.id == vessel_id))
    vessel = result.scalar_one_or_none()
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")
    return vessel


@router.get("/{vessel_id}/telemetry", response_model=list[TelemetryResponse])
async def get_vessel_telemetry(
    vessel_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[VesselTelemetry]:
    result = await db.execute(
        select(VesselTelemetry)
        .where(VesselTelemetry.vessel_id == vessel_id)
        .order_by(VesselTelemetry.timestamp.desc())
        .limit(24)
    )
    return list(result.scalars().all())


@router.get("/{vessel_id}/route", response_model=RouteResponse | None)
async def get_vessel_route(
    vessel_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Route | None:
    result = await db.execute(
        select(Route).where(Route.vessel_id == vessel_id).order_by(Route.departure_time.desc()).limit(1)
    )
    return result.scalar_one_or_none()


async def vessel_websocket(websocket: WebSocket, vessel_id: int) -> None:
    token = websocket.query_params.get("token")
    auth = ws_authenticate(token)
    if not auth:
        await websocket.close(code=4001)
        return

    channel = f"vessel:{vessel_id}"
    await vessel_manager.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        vessel_manager.disconnect(channel, websocket)


async def broadcast_vessel_update(vessel_id: int, data: dict) -> None:
    await vessel_manager.broadcast(f"vessel:{vessel_id}", {"type": "telemetry_update", "data": data})


async def simulate_vessel_movement() -> None:
    """Background task to simulate vessel movement for demo."""
    import asyncio
    import math
    from datetime import datetime, timezone

    while True:
        async with async_session() as db:
            from app.models import VesselStatus

            result = await db.execute(select(Vessel).where(Vessel.status == VesselStatus.moving))
            vessels = result.scalars().all()
            for vessel in vessels:
                vessel.latitude += 0.0001 * math.sin(vessel.id)
                vessel.longitude += 0.0002
                vessel.current_speed = 18.5 + math.sin(datetime.now().timestamp() / 60) * 2

                telemetry = VesselTelemetry(
                    vessel_id=vessel.id,
                    speed=vessel.current_speed,
                    latitude=vessel.latitude,
                    longitude=vessel.longitude,
                    fuel_level=75.0 - (vessel.id * 2),
                    engine_status={"main": "running", "aux": "standby"},
                    timestamp=datetime.now(timezone.utc),
                )
                db.add(telemetry)
                await db.commit()

                await broadcast_vessel_update(
                    vessel.id,
                    {
                        "latitude": vessel.latitude,
                        "longitude": vessel.longitude,
                        "speed": vessel.current_speed,
                        "status": vessel.status.value,
                        "timestamp": telemetry.timestamp.isoformat(),
                    },
                )
        await asyncio.sleep(5)
