from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta

from api.database import get_db
from api.models import Order, OrderStatus, Product, User
from api.schemas import OrderResponse, OrderStatusUpdate
from api.dependencies import verify_admin_token

router = APIRouter()

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    status: str = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    admin=Depends(verify_admin_token)
):
    query = select(Order).where(Order.created_at >= datetime.utcnow() - timedelta(days=days))
    if status:
        query = query.where(Order.status == status)
    result = await db.execute(query.order_by(Order.created_at.desc()).limit(100))
    return result.scalars().all()

@router.patch("/orders/{order_id}/status")
async def update_status(
    order_id: int,
    update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(verify_admin_token)
):
    await db.execute(update(Order).where(Order.id == order_id).values(status=update.status, updated_at=datetime.utcnow()))
    await db.commit()
    return {"status": "updated", "order_id": order_id}

@router.get("/dashboard")
async def dashboard_stats(db: AsyncSession = Depends(get_db), admin=Depends(verify_admin_token)):
    today = datetime.utcnow().date()
    new_orders = await db.execute(select(func.count(Order.id)).where(func.date(Order.created_at) == today, Order.status == OrderStatus.PENDING))
    revenue = await db.execute(select(func.sum(Order.final_amount)).where(Order.status == OrderStatus.DELIVERED, Order.created_at >= datetime.utcnow() - timedelta(days=30)))

    return {
        "new_orders_today": new_orders.scalar() or 0,
        "month_revenue": float(revenue.scalar() or 0)
    }
