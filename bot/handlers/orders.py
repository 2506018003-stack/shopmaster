from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from api.database import AsyncSessionLocal
from api.models import Order

router = Router()

@router.message(F.text == "📦 Мои заказы")
async def show_orders(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.user_id == message.from_user.id).order_by(Order.created_at.desc())
        )
        orders = result.scalars().all()

        if not orders:
            await message.answer("📭 У вас пока нет заказов.")
            return

        text = "📦 <b>Ваша история заказов:</b>\n\n"
        for order in orders:
            status_emoji = {"pending": "⏳", "processing": "📦", "shipped": "🚚", "delivered": "✅", "cancelled": "❌"}
            text += f"#{order.id} {status_emoji.get(order.status.value, "❓")} {order.status.value.upper()} — {order.final_amount} ₽\n"
            text += f"   📍 {order.shipping_address[:30]}...\n\n"

        await message.answer(text)
