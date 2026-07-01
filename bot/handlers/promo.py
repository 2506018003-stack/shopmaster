from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select
from api.database import AsyncSessionLocal
from api.models import PromoCode
from bot.config import settings

router = Router()

@router.message(Command("promo"))
async def create_promo(message: Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return

    # Формат: /promo CODE TYPE VALUE LIMIT [MIN_AMOUNT] [MAX_DISCOUNT]
    args = message.text.split()[1:]
    if len(args) < 4:
        await message.answer(
            "🎁 <b>Создание промокода</b>\n\n"
            "Формат: <code>/promo КОД ТИП ЗНАЧЕНИЕ ЛИМИТ [МИН_СУММА] [МАКС_СКИДКА]</code>\n\n"
            "Примеры:\n"
            "<code>/promo SALE2024 percent 20 100</code> — 20% скидка, 100 использований\n"
            "<code>/promo MINUS500 fixed 500 50 3000</code> — 500₽ скидка от 3000₽"
        )
        return

    code, discount_type, discount_value, usage_limit = args[0], args[1], float(args[2]), int(args[3])
    min_amount = float(args[4]) if len(args) > 4 else 0
    max_discount = float(args[5]) if len(args) > 5 else None

    async with AsyncSessionLocal() as session:
        promo = PromoCode(
            code=code.upper(),
            discount_type=discount_type,
            discount_value=discount_value,
            usage_limit=usage_limit,
            min_order_amount=min_amount,
            max_discount=max_discount
        )
        session.add(promo)
        await session.commit()

    await message.answer(f"✅ Промокод <code>{code.upper()}</code> создан!")

@router.message(Command("promos"))
async def list_promos(message: Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PromoCode).order_by(PromoCode.created_at.desc()))
        promos = result.scalars().all()

        text = "🎁 <b>Активные промокоды:</b>\n\n"
        for p in promos:
            status = "✅" if p.is_active else "❌"
            text += f"{status} <code>{p.code}</code> — {p.discount_value}{'%' if p.discount_type == 'percent' else '₽'} ({p.used_count}/{p.usage_limit})\n"

        await message.answer(text)
