from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from api.database import AsyncSessionLocal
from api.models import CartItem

router = Router()

@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CartItem).where(CartItem.user_id == message.from_user.id)
        )
        items = result.scalars().all()

        if not items:
            await message.answer(
                "🛒 <b>Ваша корзина пуста</b>\n\nПерейдите в каталог, чтобы добавить товары.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🛍 Перейти в каталог", callback_data="open_catalog")]
                ])
            )
            return

        total = 0
        text = "🛒 <b>Ваша корзина:</b>\n\n"
        kb_rows = []

        for item in items:
            subtotal = float(item.product.price) * item.quantity
            total += subtotal
            text += f"• {item.product.name} x{item.quantity} = {subtotal:.0f} ₽\n"
            kb_rows.append([InlineKeyboardButton(text=f"❌ {item.product.name}", callback_data=f"remove_cart:{item.id}")])

        kb_rows.append([InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout_start")])
        kb_rows.append([InlineKeyboardButton(text="🎁 Применить промокод", callback_data="apply_promo")])

        text += f"\n<b>Итого: {total:.0f} ₽</b>"

        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
