from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from bot.config import settings

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="📦 Мои заказы"), KeyboardButton(text="🏪 Магазин", web_app=WebAppInfo(url=settings.WEBAPP_URL))],
            [KeyboardButton(text="📞 Поддержка")]
        ],
        resize_keyboard=True
    )
