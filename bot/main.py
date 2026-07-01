import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from redis.asyncio import Redis, ConnectionPool

from bot.config import settings
from bot.handlers import start, catalog, cart, checkout, orders, admin, promo
from bot.middlewares.db import DbMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def main():
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
        orders.router,
        admin.router,
        promo.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started. Webhook cleared. Polling...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await redis_pool.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
