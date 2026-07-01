from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert

from api.database import AsyncSessionLocal
from api.models import CartItem, Product, Order, OrderItem, OrderStatus
from bot.config import settings

router = Router()

class CheckoutState(StatesGroup):
    promo = State()
    address = State()
    phone = State()
    confirm = State()

@router.callback_query(F.data == "checkout_start")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutState.promo)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_promo")],
        [InlineKeyboardButton(text="🎁 Ввести промокод", callback_data="enter_promo")]
    ])
    await callback.message.answer("🎁 У вас есть промокод?", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "skip_promo")
async def skip_promo(callback: CallbackQuery, state: FSMContext):
    await state.update_data(promo_code=None, discount=0)
    await state.set_state(CheckoutState.address)
    await callback.message.answer("📍 <b>Шаг 1/3</b>\n\nВведите адрес доставки:")
    await callback.answer()

@router.callback_query(F.data == "enter_promo")
async def enter_promo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CheckoutState.promo)
    await callback.message.answer("🎁 Введите промокод:")
    await callback.answer()

@router.message(CheckoutState.promo)
async def process_promo(message: Message, state: FSMContext):
    code = message.text.upper().strip()

    async with AsyncSessionLocal() as session:
        from api.models import PromoCode
        result = await session.execute(select(PromoCode).where(PromoCode.code == code, PromoCode.is_active == True))
        promo = result.scalar_one_or_none()

        if not promo:
            await message.answer("❌ Промокод не найден. Попробуйте ещё раз или нажмите /skip")
            return

        # Проверяем корзину на сумму
        cart_result = await session.execute(select(CartItem).where(CartItem.user_id == message.from_user.id))
        items = cart_result.scalars().all()
        total = sum(float(i.product.price) * i.quantity for i in items)

        if float(total) < float(promo.min_order_amount):
            await message.answer(f"❌ Минимальная сумма для промокода: {promo.min_order_amount} ₽")
            return

        discount = float(total) * (float(promo.discount_value) / 100) if promo.discount_type == "percent" else float(promo.discount_value)
        if promo.max_discount:
            discount = min(discount, float(promo.max_discount))

        await state.update_data(promo_code=code, discount=round(discount, 2), promo_id=promo.id)
        await message.answer(f"✅ Промокод применён! Скидка: {discount:.0f} ₽")

    await state.set_state(CheckoutState.address)
    await message.answer("📍 <b>Шаг 2/3</b>\n\nВведите адрес доставки:")

@router.message(CheckoutState.address)
async def process_address(message: Message, state: FSMContext):
    if len(message.text) < 10:
        await message.answer("❌ Адрес слишком короткий. Введите полный адрес.")
        return

    await state.update_data(address=message.text)
    await state.set_state(CheckoutState.phone)
    await message.answer("📱 <b>Шаг 3/3</b>\n\nВведите номер телефона:")

@router.message(CheckoutState.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if len(phone) < 10:
        await message.answer("❌ Некорректный номер. Попробуйте ещё раз.")
        return

    await state.update_data(phone=phone)
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CartItem).where(CartItem.user_id == message.from_user.id))
        items = result.scalars().all()
        total = sum(float(i.product.price) * i.quantity for i in items)
        discount = data.get("discount", 0)
        final = max(total - discount, 0)

    text = (
        f"📋 <b>Подтвердите заказ:</b>\n\n"
        f"📍 Адрес: <code>{data['address']}</code>\n"
        f"📱 Телефон: <code>{data['phone']}</code>\n"
    )
    if discount > 0:
        text += f"🎁 Скидка: <b>{discount:.0f} ₽</b>\n"
    text += f"\n💰 <b>Сумма к оплате: {final:.0f} ₽</b>"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")]
    ])

    await message.answer(text, reply_markup=kb)
    await state.set_state(CheckoutState.confirm)

@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(CartItem, Product)
                .join(Product)
                .where(CartItem.user_id == user_id)
                .with_for_update()
            )
            items = result.all()

            if not items:
                await callback.message.answer("❌ Корзина пуста.")
                await state.clear()
                return

            total = 0
            for cart_item, product in items:
                available = product.stock - product.reserved
                if cart_item.quantity > available:
                    await callback.message.answer(f"❌ {product.name} закончился. Доступно: {available} шт.")
                    await session.rollback()
                    await state.clear()
                    return
                total += float(product.price) * cart_item.quantity
                product.reserved += cart_item.quantity

            discount = data.get("discount", 0)
            final = max(total - discount, 0)

            order = Order(
                user_id=user_id,
                total_amount=total,
                final_amount=final,
                discount_amount=discount,
                shipping_address=data["address"],
                phone=data["phone"],
                status=OrderStatus.PENDING,
                promo_code_id=data.get("promo_id")
            )
            session.add(order)
            await session.flush()

            for cart_item, product in items:
                session.add(OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    price=product.price
                ))

            await session.execute(delete(CartItem).where(CartItem.user_id == user_id))

    await state.clear()

    from aiogram.types import LabeledPrice
    prices = [LabeledPrice(label="Заказ", amount=int(final * 100))]

    await callback.message.answer_invoice(
        title=f"Заказ #{order.id}",
        description=f"Оплата заказа на сумму {final:.0f} ₽",
        payload=str(order.id),
        provider_token=settings.PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        need_name=True,
        need_phone_number=True
    )

    await callback.message.answer(f"✅ <b>Заказ #{order.id} создан!</b>\n\n💳 Нажмите кнопку выше для оплаты.")

@router.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.id == int(query.invoice_payload), Order.status == OrderStatus.PENDING)
        )
        order = result.scalar_one_or_none()
        if not order:
            await query.answer(ok=False, error_message="Заказ не найден или уже оплачен")
            return
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment = message.successful_payment
    order_id = int(payment.invoice_payload)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(Order).where(Order.id == order_id).with_for_update())
            order = result.scalar_one()

            if order.status != OrderStatus.PENDING:
                return

            order.status = OrderStatus.PROCESSING
            order.telegram_payment_charge_id = payment.telegram_payment_charge_id

            items_result = await session.execute(select(OrderItem).where(OrderItem.order_id == order_id))
            for item in items_result.scalars():
                product = item.product
                product.stock -= item.quantity
                product.reserved -= item.quantity

    await message.answer(f"🎉 <b>Оплата прошла успешно!</b>\n\nЗаказ #{order_id} принят в обработку.")
