from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models import (
    EmergencyStatus,
    NotificationPriority,
    NotificationType,
    UserRole,
    VesselStatus,
)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int | None = None


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    phone: str | None = None
    cabin_number: str | None = None
    role: UserRole = UserRole.passenger
    vessel_id: int | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    full_name: str
    phone: str | None
    cabin_number: str | None
    vessel_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VesselResponse(BaseModel):
    id: int
    name: str
    type: str
    capacity: int
    current_speed: float
    latitude: float
    longitude: float
    status: VesselStatus
    captain_id: int | None
    technical_info: dict[str, Any] | None
    passenger_count: int
    weather_info: dict[str, Any] | None

    model_config = {"from_attributes": True}


class RouteResponse(BaseModel):
    id: int
    vessel_id: int
    departure_port: str
    arrival_port: str
    departure_time: datetime
    estimated_arrival: datetime
    waypoints: list[dict[str, Any]] | None

    model_config = {"from_attributes": True}


class TelemetryResponse(BaseModel):
    id: int
    vessel_id: int
    speed: float
    latitude: float
    longitude: float
    fuel_level: float | None
    engine_status: dict[str, Any] | None
    timestamp: datetime

    model_config = {"from_attributes": True}


class NotificationCreate(BaseModel):
    vessel_id: int = Field(gt=0, description="ID судна")
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    type: NotificationType = NotificationType.general
    priority: NotificationPriority = NotificationPriority.low
    scheduled_at: datetime | None = None
    requires_acknowledgment: bool = False


class EmergencyNotificationCreate(BaseModel):
    vessel_id: int = Field(gt=0, description="ID судна")
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    priority: NotificationPriority = NotificationPriority.critical
    instructions: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "vessel_id": 7,
                "title": "УЧЕБНАЯ ТРЕВОГА",
                "content": "Следуйте инструкциям экипажа",
                "priority": "critical",
                "instructions": "Соберитесь на палубе 2",
            }
        }
    }


class NotificationResponse(BaseModel):
    id: int
    vessel_id: int
    sender_id: int | None
    title: str
    content: str
    type: NotificationType
    priority: NotificationPriority
    created_at: datetime
    scheduled_at: datetime | None
    requires_acknowledgment: bool
    is_read: bool = False

    model_config = {"from_attributes": True}


class EmergencyRequestCreate(BaseModel):
    location: str
    notes: str | None = None


class EmergencyRequestUpdate(BaseModel):
    status: EmergencyStatus
    notes: str | None = None


class EmergencyRequestResponse(BaseModel):
    id: int
    passenger_id: int
    vessel_id: int
    location: str
    status: EmergencyStatus
    created_at: datetime
    resolved_at: datetime | None
    assigned_to: int | None
    notes: str | None
    passenger_name: str | None = None
    passenger_cabin: str | None = None
    passenger_phone: str | None = None

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
