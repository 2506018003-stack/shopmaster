from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from redis.asyncio import Redis

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, rate_limit: int = 1):
        self.redis = redis
        self.rate_limit = rate_limit

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        key = f"throttle:{user_id}"

        current = await self.redis.get(key)
        if current:
            await event.answer("⏳ Пожалуйста, подождите немного...")
            return

        await self.redis.setex(key, self.rate_limit, "1")
        return await handler(event, data)
