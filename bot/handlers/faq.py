from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()

FAQ_TEXT = """
<b>❓ Частые вопросы (FAQ)</b>

<b>🛍 Как сделать заказ?</b>
1. Нажмите «🛍 Каталог» или «🏪 Магазин»
2. Выберите товар и нажмите «🛒 В корзину»
3. Перейдите в корзину и нажмите «Оформить заказ»
4. Введите адрес и телефон
5. Оплатите через Telegram

<b>🎁 Как применить промокод?</b>
При оформлении заказа бот спросит промокод. Введите код, например:
<code>SALE2024</code>

<b>📦 Как отследить заказ?</b>
Нажмите «📦 Мои заказы» — там статус каждого заказа:
⏳ Ожидает → 📦 В обработке → 🚚 Отправлен → ✅ Доставлен

<b>💰 Какие способы оплаты?</b>
Оплата картой прямо в Telegram через защищённую систему.

<b>🌍 Как сменить язык?</b>
Отправьте: /lang

<b>📞 Как связаться с поддержкой?</b>
Нажмите «📞 Поддержка» или напишите @support_manager

<b>⏰ Время работы поддержки:</b>
Ежедневно с 9:00 до 21:00 МСК
"""

@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def show_faq(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Написать в поддержку", url="https://t.me/support_manager")],
        [InlineKeyboardButton(text="🛍 Перейти в каталог", callback_data="open_catalog")]
    ])
    await message.answer(FAQ_TEXT, reply_markup=kb)

@router.message(Command("lang"))
async def change_lang(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz")]
    ])
    await message.answer("🌍 <b>Выберите язык:</b>", reply_markup=kb)