from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.database import get_db
from api.models import Product, Category
from api.schemas import ProductResponse, ProductBase
from api.dependencies import verify_admin_token

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    category_id: int = None,
    search: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).where(Product.is_active == True)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    result = await db.execute(query.order_by(Product.id))
    return result.scalars().all()

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductBase,
    db: AsyncSession = Depends(get_db),
    admin=Depends(verify_admin_token)
):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.patch("/{product_id}")
async def update_product(
    product_id: int,
    product: ProductBase,
    db: AsyncSession = Depends(get_db),
    admin=Depends(verify_admin_token)
):
    await db.execute(update(Product).where(Product.id == product_id).values(**product.model_dump()))
    await db.commit()
    return {"updated": product_id}
