from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, update
from api.database import AsyncSessionLocal
from api.models import Order, OrderStatus
from bot.config import settings

router = Router()

def admin_filter(message: Message):
    return message.from_user.id in settings.ADMIN_IDS

@router.message(F.text == "🔧 Админ-панель", admin_filter)
async def admin_panel(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Новые заказы", callback_data="admin:pending")],
        [InlineKeyboardButton(text="🔄 В обработке", callback_data="admin:processing")],
        [InlineKeyboardButton(text="📊 Экспорт в Excel", url=f"{settings.CRM_URL}/export/excel")],
        [InlineKeyboardButton(text="📄 Экспорт в CSV", url=f"{settings.CRM_URL}/export/csv")],
        [InlineKeyboardButton(text="🌐 Открыть CRM", url=settings.CRM_URL)]
    ])
    await message.answer("🔧 <b>Панель управления</b>", reply_markup=kb)

@router.callback_query(F.data.startswith("admin:"))
async def admin_orders(callback: CallbackQuery):
    _, status = callback.data.split(":")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.status == status).order_by(Order.created_at.desc()).limit(10)
        )
        orders = result.scalars().all()

        if not orders:
            await callback.answer("Нет заказов")
            return

        for order in orders:
            text = (
                f"📦 <b>Заказ #{order.id}</b>\n"
                f"👤 {order.user_id} | 💰 {order.final_amount} ₽\n"
                f"📍 {order.shipping_address}\n"
                f"📱 {order.phone}"
            )

            actions = []
            if status == "pending":
                actions.append(InlineKeyboardButton(text="✅ В обработку", callback_data=f"status:{order.id}:processing"))
            elif status == "processing":
                actions.append(InlineKeyboardButton(text="🚚 Отправлен", callback_data=f"status:{order.id}:shipped"))
            elif status == "shipped":
                actions.append(InlineKeyboardButton(text="✅ Доставлен", callback_data=f"status:{order.id}:delivered"))

            actions.append(InlineKeyboardButton(text="✈️ В CRM", callback_data=f"crm_sync:{order.id}"))

            kb = InlineKeyboardMarkup(inline_keyboard=[actions])
            await callback.message.answer(text, reply_markup=kb)

    await callback.answer()

@router.callback_query(F.data.startswith("status:"))
async def update_status(callback: CallbackQuery):
    _, order_id, new_status = callback.data.split(":")
    order_id = int(order_id)

    async with AsyncSessionLocal() as session:
        await session.execute(update(Order).where(Order.id == order_id).values(status=new_status))
        await session.commit()

    await callback.answer("Статус обновлён!")
    await callback.message.edit_text(callback.message.text + "\n\n✅ Статус изменён")
