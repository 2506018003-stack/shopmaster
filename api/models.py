from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, 
    ForeignKey, Enum, Boolean, Text, BigInteger, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, validates
from datetime import datetime
import enum
from api.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    lang = Column(String(10), default="ru")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_admin = Column(Boolean, default=False)
    orders = relationship("Order", back_populates="user", lazy="selectin")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True)
    products = relationship("Product", back_populates="category", lazy="selectin")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    reserved = Column(Integer, default=0, nullable=False)
    image_url = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    is_active = Column(Boolean, default=True, index=True)

    __table_args__ = (
        CheckConstraint('stock >= 0', name='check_stock_non_negative'),
        CheckConstraint('reserved >= 0', name='check_reserved_non_negative'),
        CheckConstraint('reserved <= stock', name='check_reserved_not_exceed_stock'),
    )

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product", lazy="joined")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    final_amount = Column(Numeric(10, 2), nullable=False)
    shipping_address = Column(Text, nullable=False)
    phone = Column(String(50), nullable=False)
    payment_id = Column(String(255), unique=True, index=True)
    telegram_payment_charge_id = Column(String(255))
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders", lazy="selectin")
    items = relationship("OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan")
    promo_code = relationship("PromoCode", back_populates="orders")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", lazy="joined")

class PromoCode(Base):
    __tablename__ = "promo_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_type = Column(String(20), nullable=False, default="percent")
    discount_value = Column(Numeric(10, 2), nullable=False)
    min_order_amount = Column(Numeric(10, 2), default=0)
    max_discount = Column(Numeric(10, 2), nullable=True)
    usage_limit = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="promo_code")

class PromoUsage(Base):
    __tablename__ = "promo_usages"
    id = Column(Integer, primary_key=True)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), index=True)
    user_id = Column(BigInteger, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    used_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('promo_code_id', 'user_id', name='unique_user_promo'),
    )
