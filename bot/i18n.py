from typing import Dict
from dataclasses import dataclass

@dataclass
class Translations:
    welcome: str
    catalog: str
    cart: str
    orders: str
    support: str
    admin_panel: str
    back: str
    confirm: str
    cancel: str
    total: str
    empty_cart: str
    order_created: str
    order_paid: str
    order_shipped: str
    order_delivered: str
    promo_applied: str
    promo_invalid: str
    enter_address: str
    enter_phone: str
    confirm_order: str
    payment_success: str
    new_order_notification: str
    status_updated: str
    stats_new_orders: str
    stats_processing: str
    stats_revenue: str
    sync_complete: str
    sync_error: str

TRANSLATIONS: Dict[str, Translations] = {
    "ru": Translations(
        welcome="👋 Привет, <b>{name}</b>!\n\nДобро пожаловать в <b>ShopMaster</b>",
        catalog="🛍 Каталог",
        cart="🛒 Корзина",
        orders="📦 Мои заказы",
        support="📞 Поддержка",
        admin_panel="🔧 Админ-панель",
        back="⬅️ Назад",
        confirm="✅ Подтвердить",
        cancel="❌ Отменить",
        total="Итого",
        empty_cart="🛒 Ваша корзина пуста",
        order_created="✅ Заказ #{order_id} создан!",
        order_paid="💰 Заказ оплачен!",
        order_shipped="🚚 Заказ отправлен!",
        order_delivered="🎉 Заказ доставлен!",
        promo_applied="✅ Промокод применён: скидка {discount} ₽",
        promo_invalid="❌ {message}",
        enter_address="📍 Введите адрес доставки:",
        enter_phone="📱 Введите номер телефона:",
        confirm_order="📋 Подтвердите заказ:",
        payment_success="🎉 Оплата прошла успешно!",
        new_order_notification="💰 <b>Новая оплата!</b>\n\nЗаказ #{order_id}\nСумма: {amount} ₽",
        status_updated="✅ Статус обновлён",
        stats_new_orders="Новые",
        stats_processing="В работе",
        stats_revenue="₽ сегодня",
        sync_complete="✈️ Заявки синхронизированы",
        sync_error="❌ Ошибка синхронизации"
    ),
    "en": Translations(
        welcome="👋 Hello, <b>{name}</b>!\n\nWelcome to <b>ShopMaster</b>",
        catalog="🛍 Catalog",
        cart="🛒 Cart",
        orders="📦 My Orders",
        support="📞 Support",
        admin_panel="🔧 Admin Panel",
        back="⬅️ Back",
        confirm="✅ Confirm",
        cancel="❌ Cancel",
        total="Total",
        empty_cart="🛒 Your cart is empty",
        order_created="✅ Order #{order_id} created!",
        order_paid="💰 Order paid!",
        order_shipped="🚚 Order shipped!",
        order_delivered="🎉 Order delivered!",
        promo_applied="✅ Promo applied: {discount} ₽ off",
        promo_invalid="❌ {message}",
        enter_address="📍 Enter delivery address:",
        enter_phone="📱 Enter phone number:",
        confirm_order="📋 Confirm your order:",
        payment_success="🎉 Payment successful!",
        new_order_notification="💰 <b>New payment!</b>\n\nOrder #{order_id}\nAmount: {amount} ₽",
        status_updated="✅ Status updated",
        stats_new_orders="New",
        stats_processing="Processing",
        stats_revenue="₽ today",
        sync_complete="✈️ Sync complete",
        sync_error="❌ Sync error"
    ),
    "uz": Translations(
        welcome="👋 Salom, <b>{name}</b>!\n\n<b>ShopMaster</b>ga xush kelibsiz",
        catalog="🛍 Katalog",
        cart="🛒 Savat",
        orders="📦 Buyurtmalarim",
        support="📞 Qo'llab-quvvatlash",
        admin_panel="🔧 Admin panel",
        back="⬅️ Orqaga",
        confirm="✅ Tasdiqlash",
        cancel="❌ Bekor qilish",
        total="Jami",
        empty_cart="🛒 Savatingiz bo'sh",
        order_created="✅ Buyurtma #{order_id} yaratildi!",
        order_paid="💰 Buyurtma to'landi!",
        order_shipped="🚚 Buyurtma jo'natildi!",
        order_delivered="🎉 Buyurtma yetkazildi!",
        promo_applied="✅ Promo-kod qo'llandi: {discount} ₽ chegirma",
        promo_invalid="❌ {message}",
        enter_address="📍 Yetkazib berish manzilini kiriting:",
        enter_phone="📱 Telefon raqamingizni kiriting:",
        confirm_order="📋 Buyurtmani tasdiqlang:",
        payment_success="🎉 To'lov muvaffaqiyatli!",
        new_order_notification="💰 <b>Yangi to'lov!</b>\n\nBuyurtma #{order_id}\nSumma: {amount} ₽",
        status_updated="✅ Status yangilandi",
        stats_new_orders="Yangi",
        stats_processing="Ishlanmoqda",
        stats_revenue="₽ bugun",
        sync_complete="✈️ Sinxronlash yakunlandi",
        sync_error="❌ Sinxronlash xatosi"
    )
}

class I18n:
    def __init__(self, lang: str = "ru"):
        self.lang = lang if lang in TRANSLATIONS else "ru"
        self.t = TRANSLATIONS[self.lang]

    def get(self, key: str, **kwargs) -> str:
        value = getattr(self.t, key, key)
        return value.format(**kwargs) if kwargs else value

def get_user_lang(user_id: int) -> str:
    return "ru"

def set_user_lang(user_id: int, lang: str):
    pass
