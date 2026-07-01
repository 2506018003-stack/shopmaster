from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def pagination_buttons(current_page: int, total_pages: int, prefix: str):
    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}:{current_page-1}"))
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}:{current_page+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons]) if buttons else None
