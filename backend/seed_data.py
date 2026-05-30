import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.database import Base
from app.models import (
    EmergencyRequest,
    EmergencyStatus,
    Notification,
    NotificationPriority,
    NotificationType,
    Route,
    User,
    UserRole,
    Vessel,
    VesselStatus,
    VesselTelemetry,
)
from app.services.auth_service import get_password_hash

engine = create_engine(settings.database_url_sync)
SessionLocal = sessionmaker(bind=engine)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.execute(select(Vessel)).first():
            print("Database already seeded, skipping...")
            return

        vessels_data = [
            {
                "name": "Речной вокзал",
                "type": "passenger_liner",
                "capacity": 250,
                "current_speed": 18.5,
                "latitude": 55.7558,
                "longitude": 37.6173,
                "status": VesselStatus.moving,
                "passenger_count": 180,
                "technical_info": {
                    "draft": 2.1,
                    "displacement": 1200,
                    "fuel_level": 78,
                    "engines": {"main": "running", "aux": "standby"},
                },
                "weather_info": {
                    "air_temp": 22,
                    "water_temp": 16,
                    "wind": "5 м/с СЗ",
                    "conditions": "Ясно",
                },
            },
            {
                "name": "Москва-1",
                "type": "cruise_ship",
                "capacity": 400,
                "current_speed": 15.2,
                "latitude": 56.3269,
                "longitude": 44.0075,
                "status": VesselStatus.moving,
                "passenger_count": 320,
                "technical_info": {
                    "draft": 2.8,
                    "displacement": 2100,
                    "fuel_level": 65,
                    "engines": {"main": "running", "aux": "running"},
                },
                "weather_info": {
                    "air_temp": 20,
                    "water_temp": 14,
                    "wind": "3 м/с З",
                    "conditions": "Облачно",
                },
            },
            {
                "name": "Волга-Экспресс",
                "type": "fast_ferry",
                "capacity": 120,
                "current_speed": 0,
                "latitude": 55.8304,
                "longitude": 49.0661,
                "status": VesselStatus.docked,
                "passenger_count": 45,
                "technical_info": {
                    "draft": 1.5,
                    "displacement": 450,
                    "fuel_level": 90,
                    "engines": {"main": "standby", "aux": "standby"},
                },
                "weather_info": {
                    "air_temp": 24,
                    "water_temp": 18,
                    "wind": "2 м/с Ю",
                    "conditions": "Ясно",
                },
            },
        ]

        vessels = [Vessel(**v) for v in vessels_data]
        db.add_all(vessels)
        db.flush()
        db.commit()

        vessel_ids = {i: v.id for i, v in enumerate(vessels)}

        users_data = [
            {"email": "passenger1@test.com", "password": "password123", "role": UserRole.passenger, "full_name": "Иван Петров", "cabin_number": "A-101", "phone": "+79001112233", "vessel_idx": 0},
            {"email": "passenger2@test.com", "password": "password123", "role": UserRole.passenger, "full_name": "Мария Сидорова", "cabin_number": "B-205", "phone": "+79004445566", "vessel_idx": 0},
            {"email": "passenger3@test.com", "password": "password123", "role": UserRole.passenger, "full_name": "Алексей Козлов", "cabin_number": "A-105", "phone": "+79007778899", "vessel_idx": 0},
            {"email": "passenger4@test.com", "password": "password123", "role": UserRole.passenger, "full_name": "Елена Новикова", "cabin_number": "C-301", "phone": "+79001234567", "vessel_idx": 1},
            {"email": "passenger5@test.com", "password": "password123", "role": UserRole.passenger, "full_name": "Дмитрий Волков", "cabin_number": "D-102", "phone": "+79007654321", "vessel_idx": 1},
            {"email": "captain@ship.com", "password": "captain123", "role": UserRole.crew, "full_name": "Капитан Смирнов", "phone": "+79009998877", "vessel_idx": 0},
            {"email": "crew1@ship.com", "password": "crew123", "role": UserRole.crew, "full_name": "Помощник капитана Орлов", "phone": "+79005556677", "vessel_idx": 0},
            {"email": "crew2@ship.com", "password": "crew123", "role": UserRole.crew, "full_name": "Старший механик Белов", "phone": "+79003334455", "vessel_idx": 1},
        ]

        for i in range(6, 21):
            users_data.append({
                "email": f"passenger{i}@test.com",
                "password": "password123",
                "role": UserRole.passenger,
                "full_name": f"Пассажир {i}",
                "cabin_number": f"A-{100 + i}",
                "phone": f"+7900{i:07d}",
                "vessel_idx": 0 if i % 2 == 0 else 1,
            })

        users = []
        for u in users_data:
            users.append(User(
                email=u["email"],
                password_hash=get_password_hash(u["password"]),
                role=u["role"],
                full_name=u["full_name"],
                cabin_number=u.get("cabin_number"),
                phone=u.get("phone"),
                vessel_id=vessel_ids[u["vessel_idx"]],
            ))
        db.add_all(users)
        db.flush()

        vessels[0].captain_id = users[5].id

        vid0, vid1, vid2 = vessels[0].id, vessels[1].id, vessels[2].id

        waypoints_moscow_uglich = [
            {"lat": 55.7558, "lng": 37.6173, "name": "Северный речной вокзал"},
            {"lat": 55.85, "lng": 37.5, "name": "Химки"},
            {"lat": 56.0, "lng": 37.2, "name": "Дубна"},
            {"lat": 56.5, "lng": 37.0, "name": "Дмитров"},
            {"lat": 57.0, "lng": 38.0, "name": "Кalyazin"},
            {"lat": 57.5, "lng": 38.5, "name": "Углич"},
        ]

        now = datetime.now(timezone.utc)
        routes_data = [
            {
                "vessel_id": vessels[0].id,
                "departure_port": "Москва (Северный речной вокзал)",
                "arrival_port": "Углич",
                "departure_time": now - timedelta(hours=2),
                "estimated_arrival": now + timedelta(hours=6),
                "waypoints": waypoints_moscow_uglich,
            },
            {
                "vessel_id": vessels[1].id,
                "departure_port": "Нижний Новгород",
                "arrival_port": "Казань",
                "departure_time": now - timedelta(hours=4),
                "estimated_arrival": now + timedelta(hours=8),
                "waypoints": [
                    {"lat": 56.3269, "lng": 44.0075, "name": "Нижний Новгород"},
                    {"lat": 56.0, "lng": 45.0, "name": "Чебоксары"},
                    {"lat": 55.83, "lng": 49.07, "name": "Казань"},
                ],
            },
            {
                "vessel_id": vessels[2].id,
                "departure_port": "Казань",
                "arrival_port": "Самара",
                "departure_time": now + timedelta(hours=2),
                "estimated_arrival": now + timedelta(hours=14),
                "waypoints": [
                    {"lat": 55.83, "lng": 49.07, "name": "Казань"},
                    {"lat": 55.5, "lng": 50.0, "name": "Тетюши"},
                    {"lat": 53.2, "lng": 50.15, "name": "Самара"},
                ],
            },
        ]
        db.add_all([Route(**r) for r in routes_data])

        notifications_data = [
            {"vessel_id": vid0, "sender_id": users[5].id, "title": "Обед в ресторане", "content": "Обед подаётся с 12:00 до 14:00 в ресторане на палубе 3.", "type": NotificationType.general, "priority": NotificationPriority.low},
            {"vessel_id": vid0, "sender_id": users[5].id, "title": "Приближаемся к причалу", "content": "Через 30 минут причаливание в Химки. Просим подготовиться.", "type": NotificationType.general, "priority": NotificationPriority.medium},
            {"vessel_id": vid0, "sender_id": users[6].id, "title": "Развлекательная программа", "content": "Концерт в салоне в 19:00. Приглашаем всех пассажиров!", "type": NotificationType.general, "priority": NotificationPriority.low},
            {"vessel_id": vid0, "sender_id": users[5].id, "title": "Изменение расписания", "content": "Прибытие в Углич переносится на 1 час.", "type": NotificationType.general, "priority": NotificationPriority.high},
            {"vessel_id": vid1, "sender_id": users[7].id, "title": "Экскурсия", "content": "Экскурсия по городу в 15:00. Сбор у трапа.", "type": NotificationType.general, "priority": NotificationPriority.medium},
        ]
        for i in range(5, 15):
            notifications_data.append({
                "vessel_id": vid0 if i % 2 == 0 else vid1,
                "sender_id": users[5].id,
                "title": f"Объявление #{i}",
                "content": f"Информационное сообщение для пассажиров №{i}.",
                "type": NotificationType.general,
                "priority": NotificationPriority.low,
            })

        emergency_notifications = [
            {"vessel_id": vid0, "sender_id": users[5].id, "title": "УЧЕБНАЯ ТРЕВОГА", "content": "Это учебное оповещение. Следуйте инструкциям экипажа.", "type": NotificationType.emergency, "priority": NotificationPriority.critical, "requires_acknowledgment": True},
            {"vessel_id": vid0, "sender_id": users[5].id, "title": "Задержка рейса", "content": "Рейс задерживается на 45 минут из-за погодных условий.", "type": NotificationType.emergency, "priority": NotificationPriority.high, "requires_acknowledgment": False},
            {"vessel_id": vid1, "sender_id": users[7].id, "title": "Техническая проверка", "content": "Проводится плановая проверка систем безопасности.", "type": NotificationType.emergency, "priority": NotificationPriority.medium, "requires_acknowledgment": False},
        ]
        db.add_all([Notification(**n) for n in notifications_data + emergency_notifications])

        emergency_requests_data = [
            {"passenger_id": users[2].id, "vessel_id": vid0, "location": "Каюта A-105", "status": EmergencyStatus.pending},
            {"passenger_id": users[0].id, "vessel_id": vid0, "location": "Ресторан", "status": EmergencyStatus.resolved, "resolved_at": now - timedelta(hours=1)},
            {"passenger_id": users[1].id, "vessel_id": vid0, "location": "Палуба 2", "status": EmergencyStatus.in_progress, "assigned_to": users[6].id},
            {"passenger_id": users[3].id, "vessel_id": vid1, "location": "Каюта C-301", "status": EmergencyStatus.pending},
            {"passenger_id": users[4].id, "vessel_id": vid1, "location": "Спа-зона", "status": EmergencyStatus.resolved, "resolved_at": now - timedelta(hours=2)},
        ]
        db.add_all([EmergencyRequest(**e) for e in emergency_requests_data])

        for vessel in vessels:
            base_lat, base_lng = vessel.latitude, vessel.longitude
            for i in range(24):
                ts = now - timedelta(minutes=5 * i)
                db.add(VesselTelemetry(
                    vessel_id=vessel.id,
                    speed=max(0, vessel.current_speed + (i % 3) - 1),
                    latitude=base_lat - 0.0001 * i,
                    longitude=base_lng - 0.0002 * i,
                    fuel_level=75 - i * 0.5,
                    engine_status={"main": "running" if vessel.status == VesselStatus.moving else "standby"},
                    timestamp=ts,
                ))

        db.commit()
        print("Seed completed successfully!")
        print(f"  Vessels: {len(vessels)}")
        print(f"  Users: {len(users)}")
        print(f"  Routes: {len(routes_data)}")
        print(f"  Notifications: {len(notifications_data) + len(emergency_notifications)}")
        print(f"  Emergency requests: {len(emergency_requests_data)}")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
