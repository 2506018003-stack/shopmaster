from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)

class ProductResponse(ProductBase):
    id: int
    reserved: int = 0
    is_active: bool = True
    category: Optional[dict] = None

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, le=99)

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    name: str
    quantity: int
    price: Decimal

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    user_name: Optional[str] = None
    status: str
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    shipping_address: str
    phone: str
    created_at: datetime
    items: List[OrderItemResponse]

class OrderStatusUpdate(BaseModel):
    status: str

class PromoCodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    discount_type: str
    discount_value: Decimal
    min_order_amount: Decimal
    max_discount: Optional[Decimal]
    usage_limit: int
    used_count: int
    is_active: bool

class PromoCodeCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=50, pattern=r'^[A-Z0-9_-]+$')
    discount_type: str = Field(..., pattern=r'^(percent|fixed)$')
    discount_value: Decimal = Field(..., gt=0)
    min_order_amount: Decimal = Field(default=0, ge=0)
    max_discount: Optional[Decimal] = None
    usage_limit: int = Field(default=1, ge=1)

class ApplyPromoRequest(BaseModel):
    code: str
    order_total: Decimal

class ApplyPromoResponse(BaseModel):
    valid: bool
    discount_amount: Decimal
    final_amount: Decimal
    message: str
