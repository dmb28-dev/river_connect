from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Vessel


async def get_vessel_or_404(db: AsyncSession, vessel_id: int) -> Vessel:
    result = await db.execute(select(Vessel).where(Vessel.id == vessel_id))
    vessel = result.scalar_one_or_none()
    if not vessel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vessel {vessel_id} not found")
    return vessel


async def ensure_crew_vessel_access(crew: User, vessel_id: int) -> None:
    if crew.vessel_id and crew.vessel_id != vessel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only send notifications for your assigned vessel",
        )
