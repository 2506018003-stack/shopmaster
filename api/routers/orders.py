from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.database import get_db
from api.models import Order, OrderItem, CartItem, Product, OrderStatus
from api.schemas import OrderResponse

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    return result.scalars().all()

@router.post("/")
async def create_order_from_miniapp(data: dict, db: AsyncSession = Depends(get_db)):
    from api.dependencies import verify_telegram_init_data
    try:
        verify_telegram_init_data(data.get("init_data", ""))
    except:
        raise HTTPException(status_code=403, detail="Invalid init data")

    user_id = data.get("user_id")
    items = data.get("items", [])

    async with db.begin():
        total = 0
        order_items = []

        for item in items:
            result = await db.execute(select(Product).where(Product.id == item["id"]).with_for_update())
            product = result.scalar_one_or_none()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item['id']} not found")

            available = product.stock - product.reserved
            if item["qty"] > available:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

            product.reserved += item["qty"]
            total += float(product.price) * item["qty"]
            order_items.append({"product_id": product.id, "quantity": item["qty"], "price": product.price})

        order = Order(
            user_id=user_id,
            total_amount=total,
            final_amount=total,
            shipping_address=data.get("address", "Не указан"),
            phone=data.get("phone", "Не указан"),
            status=OrderStatus.PENDING
        )
        db.add(order)
        await db.flush()

        for oi in order_items:
            db.add(OrderItem(order_id=order.id, **oi))

        await db.execute(delete(CartItem).where(CartItem.user_id == user_id))

    return {"order_id": order.id, "total": total}
