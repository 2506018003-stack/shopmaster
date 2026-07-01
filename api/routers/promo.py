from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from api.database import get_db
from api.models import PromoCode, PromoUsage
from api.schemas import PromoCodeResponse, PromoCodeCreate, ApplyPromoRequest, ApplyPromoResponse
from api.dependencies import verify_admin_token

router = APIRouter()

def calculate_discount(promo: PromoCode, order_total: float) -> float:
    if promo.discount_type == "percent":
        discount = order_total * (float(promo.discount_value) / 100)
        if promo.max_discount:
            discount = min(discount, float(promo.max_discount))
        return round(discount, 2)
    else:
        return min(float(promo.discount_value), order_total)

@router.post("/validate", response_model=ApplyPromoResponse)
async def validate_promo(request: ApplyPromoRequest, user_id: int = None, db: AsyncSession = Depends(get_db)):
    code = request.code.upper().strip()

    result = await db.execute(select(PromoCode).where(PromoCode.code == code, PromoCode.is_active == True))
    promo = result.scalar_one_or_none()

    if not promo:
        return ApplyPromoResponse(valid=False, discount_amount=0, final_amount=request.order_total, message="Промокод не найден")

    now = datetime.utcnow()
    if promo.valid_from and now < promo.valid_from:
        return ApplyPromoResponse(valid=False, discount_amount=0, final_amount=request.order_total, message="Промокод ещё не активен")
    if promo.valid_until and now > promo.valid_until:
        return ApplyPromoResponse(valid=False, discount_amount=0, final_amount=request.order_total, message="Промокод истёк")
    if promo.used_count >= promo.usage_limit:
        return ApplyPromoResponse(valid=False, discount_amount=0, final_amount=request.order_total, message="Лимит исчерпан")
    if float(request.order_total) < float(promo.min_order_amount):
        return ApplyPromoResponse(valid=False, discount_amount=0, final_amount=request.order_total, message=f"Минимальная сумма: {promo.min_order_amount} ₽")

    if user_id:
        existing = await db.execute(select(PromoUsage).where(PromoUsage.promo_code_id == promo.id, PromoUsage.user_id == user_id))
        if existing.scalar_one_or_none():
            return ApplyPromoResponse(valid=False, discount_amount=0, final_amount=request.order_total, message="Уже использован")

    discount = calculate_discount(promo, float(request.order_total))
    final_amount = max(float(request.order_total) - discount, 0)

    return ApplyPromoResponse(valid=True, discount_amount=round(discount, 2), final_amount=round(final_amount, 2), message=f"Скидка {discount:.0f} ₽ применена!")

@router.post("/", response_model=PromoCodeResponse)
async def create_promo(promo: PromoCodeCreate, db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    new_promo = PromoCode(**promo.model_dump())
    db.add(new_promo)
    await db.commit()
    await db.refresh(new_promo)
    return new_promo

@router.get("/", response_model=List[PromoCodeResponse])
async def list_promos(db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    result = await db.execute(select(PromoCode).order_by(PromoCode.created_at.desc()))
    return result.scalars().all()
