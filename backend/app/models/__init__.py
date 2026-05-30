import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    passenger = "passenger"
    crew = "crew"


class VesselStatus(str, enum.Enum):
    moving = "moving"
    docked = "docked"
    mooring = "mooring"


class NotificationType(str, enum.Enum):
    general = "general"
    emergency = "emergency"


class NotificationPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class EmergencyStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.passenger)
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cabin_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vessel_id: Mapped[int | None] = mapped_column(ForeignKey("vessels.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    vessel: Mapped["Vessel | None"] = relationship(
        back_populates="users", foreign_keys=[vessel_id]
    )
    sent_notifications: Mapped[list["Notification"]] = relationship(back_populates="sender")
    emergency_requests: Mapped[list["EmergencyRequest"]] = relationship(
        back_populates="passenger", foreign_keys="EmergencyRequest.passenger_id"
    )


class Vessel(Base):
    __tablename__ = "vessels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(100))
    capacity: Mapped[int] = mapped_column(Integer, default=200)
    current_speed: Mapped[float] = mapped_column(Float, default=0.0)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[VesselStatus] = mapped_column(Enum(VesselStatus), default=VesselStatus.docked)
    captain_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    technical_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    passenger_count: Mapped[int] = mapped_column(Integer, default=0)
    weather_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    users: Mapped[list["User"]] = relationship(
        back_populates="vessel", foreign_keys="User.vessel_id"
    )
    captain: Mapped["User | None"] = relationship(foreign_keys=[captain_id])
    routes: Mapped[list["Route"]] = relationship(back_populates="vessel")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="vessel")
    telemetry: Mapped[list["VesselTelemetry"]] = relationship(back_populates="vessel")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"))
    departure_port: Mapped[str] = mapped_column(String(255))
    arrival_port: Mapped[str] = mapped_column(String(255))
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    estimated_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    waypoints: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    vessel: Mapped["Vessel"] = relationship(back_populates="routes")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"))
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), default=NotificationType.general)
    priority: Mapped[NotificationPriority] = mapped_column(
        Enum(NotificationPriority), default=NotificationPriority.low
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requires_acknowledgment: Mapped[bool] = mapped_column(Boolean, default=False)

    vessel: Mapped["Vessel"] = relationship(back_populates="notifications")
    sender: Mapped["User | None"] = relationship(back_populates="sent_notifications")
    reads: Mapped[list["NotificationRead"]] = relationship(back_populates="notification")


class NotificationRead(Base):
    __tablename__ = "notification_reads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    notification: Mapped["Notification"] = relationship(back_populates="reads")


class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"))
    location: Mapped[str] = mapped_column(String(255))
    status: Mapped[EmergencyStatus] = mapped_column(Enum(EmergencyStatus), default=EmergencyStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    passenger: Mapped["User"] = relationship(
        back_populates="emergency_requests", foreign_keys=[passenger_id]
    )
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assigned_to])


class VesselTelemetry(Base):
    __tablename__ = "vessel_telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"))
    speed: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    fuel_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    engine_status: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    vessel: Mapped["Vessel"] = relationship(back_populates="telemetry")
