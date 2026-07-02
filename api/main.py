import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from redis.asyncio import Redis, ConnectionPool

from api.database import engine, Base
from api.routers import products, orders, auth, admin, crm, promo, export
from bot.config import settings
from bot.handlers import start, catalog, cart, checkout, orders as bot_orders, admin as bot_admin, promo as bot_promo
from bot.middlewares.db import DbMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    redis_pool = ConnectionPool.from_url(
        str(settings.REDIS_URL),
        max_connections=50,
        decode_responses=True
    )
    redis = Redis(connection_pool=redis_pool)
    storage = RedisStorage(redis=redis)

    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)
    dp.message.middleware(ThrottlingMiddleware(redis, rate_limit=1))
    dp.callback_query.middleware(ThrottlingMiddleware(redis, rate_limit=1))
    dp.message.middleware(DbMiddleware())
    dp.callback_query.middleware(DbMiddleware())
    dp.include_routers(
        start.router,
        catalog.router,
        cart.router,
        checkout.router,
        bot_orders.router,
        bot_admin.router,
        bot_promo.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(dp.start_polling(bot))

    yield

    dp.stop_polling()
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    await bot.session.close()
    await redis_pool.disconnect()
    await engine.dispose()

app = FastAPI(
    title="ShopMaster API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("DEBUG", "false").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "false").lower() == "true" else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "shopmaster", "version": "2.0.0", "timestamp": str(datetime.utcnow())}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(crm.router, prefix="/crm", tags=["crm"])
app.include_router(promo.router, prefix="/promo", tags=["promo"])
app.include_router(export.router, prefix="/export", tags=["export"])

app.mount("/miniapp", StaticFiles(directory="miniapp", html=True), name="miniapp")
app.mount("/crm", StaticFiles(directory="crm", html=True), name="crm")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
