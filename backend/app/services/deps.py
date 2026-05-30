from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UserRole
from app.services.auth_service import decode_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == int(payload.sub)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_crew_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.crew:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Crew access required")
    return user


async def get_passenger_user(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.passenger:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Passenger access required")
    return user


def ws_authenticate(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    return {"user_id": int(payload.sub), "role": payload.role}
