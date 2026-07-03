from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, Command
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from api.database import AsyncSessionLocal
from api.models import User
from bot.config import settings
from bot.i18n import I18n, get_user_lang

router = Router()

def get_main_menu(i18n: I18n, is_admin: bool = False):
    keyboard = [
        [KeyboardButton(text=i18n.get("catalog")), KeyboardButton(text=i18n.get("cart"))],
        [KeyboardButton(text=i18n.get("orders")), KeyboardButton(text="🏪 Shop", web_app=WebAppInfo(url=settings.WEBAPP_URL))],
        [KeyboardButton(text=i18n.get("support"))]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text=i18n.get("admin_panel"))])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Select action..."
    )

@router.message(CommandStart())
async def cmd_start(message: Message):
    lang = get_user_lang(message.from_user.id)
    i18n = I18n(lang)

    async with AsyncSessionLocal() as session:
        stmt = insert(User).values(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            lang=lang
        ).on_conflict_do_nothing(index_elements=['id'])
        await session.execute(stmt)
        await session.commit()

        result = await session.execute(select(User).where(User.id == message.from_user.id))
        user = result.scalar_one()

    is_admin = message.from_user.id in settings.ADMIN_IDS
    await message.answer(
        i18n.get("welcome", name=message.from_user.first_name),
        reply_markup=get_main_menu(i18n, is_admin=is_admin)
    )

@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "🛒 <b>ShopMaster — как пользоваться</b>\n\n"
        "🛍 <b>Каталог</b> — посмотреть и выбрать товары\n"
        "🛒 <b>Корзина</b> — добавленные товары и оформление заказа\n"
        "📦 <b>Мои заказы</b> — статус и история покупок\n"
        "📞 <b>Поддержка</b> — связаться с нами\n\n"
        "Если у вас есть вопросы, напишите нам: @tgbothelp_infinityfree\n"
        "⏰ Работаем с 9:00 до 21:00 МСК"
    )

@router.message(F.text == "📞 Поддержка")
async def support_handler(message: Message):
    await message.answer(
        "📞 <b>Служба поддержки</b>\n\n"
        "Если у вас есть вопросы, напишите нам: @tgbothelp_infinityfree\n\n"
        "⏰ Работаем с 9:00 до 21:00 МСК"
    )

@router.message(Command("admin_help"))
async def admin_help_handler(message: Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    await message.answer(
        "🔧 <b>Админ-команды</b>\n\n"
        "<b>Промокоды:</b>\n"
        "<code>/promo_create КОД ТИП ЗНАЧЕНИЕ ЛИМИТ [МИН_СУММА] [МАКС_СКИДКА]</code>\n"
        "Пример: <code>/promo_create SALE2024 percent 20 100</code>\n"
        "Типы: <code>percent</code> — %, <code>fixed</code> — фикс. сумма в ₽\n\n"
        "<code>/promo_list</code> — список промокодов со статистикой\n\n"
        "<b>Заказы и статистика:</b>\n"
        "<code>/stats</code> — новые заказы, выручка, топ товаров\n"
        "<code>/export_excel</code> / <code>/export_csv</code> — выгрузка заказов\n\n"
        "<b>CRM:</b>\n"
        f"{settings.CRM_URL} — смена статуса заказа, деактивация промокодов, экспорт\n\n"
        "<b>Добавление товара</b> (через API, нужен admin JWT) — см. FAQ.md на сервере.",
        disable_web_page_preview=True
    )
