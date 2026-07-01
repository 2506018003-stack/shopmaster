import logging
from aiogram import Bot
from bot.config import settings

logger = logging.getLogger(__name__)

async def notify_user(user_id: int, text: str):
    """Placeholder - в реальности через Bot API"""
    logger.info(f"Notify user {user_id}: {text}")

async def notify_admins(text: str):
    """Placeholder - в реальности через Bot API"""
    logger.info(f"Notify admins: {text}")
