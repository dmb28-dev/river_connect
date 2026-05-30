import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, emergency, notifications, vessels
from app.config import settings
from app.services.redis_service import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(vessels.simulate_vessel_movement())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await close_redis()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(vessels.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(emergency.router, prefix="/api")

# WebSocket endpoints per spec
app.add_api_websocket_route("/ws/vessels/{vessel_id}", vessels.vessel_websocket)
app.add_api_websocket_route("/ws/notifications", notifications.notifications_websocket)
app.add_api_websocket_route("/ws/emergency", emergency.emergency_websocket)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
