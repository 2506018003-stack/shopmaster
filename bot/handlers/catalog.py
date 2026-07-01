from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from api.database import AsyncSessionLocal
from api.models import Category, Product

router = Router()
PRODUCTS_PER_PAGE = 5

@router.message(F.text == "🛍 Каталог")
async def show_catalog(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Category).where(Category.products.any(Product.is_active == True))
        )
        categories = result.scalars().all()

        if not categories:
            await message.answer("😔 Каталог временно пуст. Загляните позже!")
            return

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"📂 {cat.name}", callback_data=f"cat:{cat.id}:0")]
            for cat in categories
        ])

        await message.answer("🛍 <b>Наш каталог</b>\n\nВыберите категорию:", reply_markup=kb)

@router.callback_query(F.data.startswith("cat:"))
async def show_products(callback: CallbackQuery):
    _, cat_id, page = callback.data.split(":")
    cat_id, page = int(cat_id), int(page)
    offset = page * PRODUCTS_PER_PAGE

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product)
            .where(Product.category_id == cat_id, Product.is_active == True)
            .order_by(Product.id)
            .offset(offset)
            .limit(PRODUCTS_PER_PAGE)
        )
        products = result.scalars().all()

        if not products:
            await callback.answer("Больше товаров нет")
            return

        for product in products:
            available = product.stock - product.reserved
            text = f"<b>{product.name}</b>\n\n{product.description or ''}\n\n💰 <b>{product.price} ₽</b>\n📦 Доступно: <b>{available} шт.</b>"

            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🛒 Добавить ({product.price} ₽)", callback_data=f"add_to_cart:{product.id}:1")]
            ])

            if product.image_url:
                await callback.message.answer_photo(photo=product.image_url, caption=text, reply_markup=kb)
            else:
                await callback.message.answer(text, reply_markup=kb)

        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"cat:{cat_id}:{page-1}"))
        if len(products) == PRODUCTS_PER_PAGE:
            nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"cat:{cat_id}:{page+1}"))

        if nav_buttons:
            await callback.message.answer("Навигация:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[nav_buttons]))

    await callback.answer()

@router.callback_query(F.data.startswith("add_to_cart:"))
async def add_to_cart(callback: CallbackQuery):
    _, product_id, qty = callback.data.split(":")
    product_id, qty = int(product_id), int(qty)
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        from api.models import CartItem
        from sqlalchemy.dialects.postgresql import insert

        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one()
        available = product.stock - product.reserved

        cart_result = await session.execute(
            select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
        )
        existing = cart_result.scalar_one_or_none()
        current_qty = existing.quantity if existing else 0

        if current_qty + qty > available:
            await callback.answer(f"❌ Нельзя добавить больше {available} шт.", show_alert=True)
            return

        stmt = insert(CartItem).values(
            user_id=user_id, product_id=product_id, quantity=current_qty + qty
        ).on_conflict_do_update(
            index_elements=['user_id', 'product_id'],
            set_=dict(quantity=CartItem.quantity + qty)
        )
        await session.execute(stmt)
        await session.commit()

    await callback.answer("✅ Добавлено в корзину!")
