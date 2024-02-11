from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton


def kb_generation(data: str|list, location=False, id=False, one_time=False) -> ReplyKeyboardBuilder: 
    
    builder = ReplyKeyboardBuilder()

    if isinstance(data, str):
        data = [data]
    elif location:
        builder.add(KeyboardButton(text=data, request_location=True))
        return builder.as_markup(resize_keyboard=True)
    
    [builder.add(KeyboardButton(text=i)) for i in data]

    if id:
        return [builder.as_markup(resize_keyboard=True), id]
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=one_time)


def like_dislike_kb(id_match: str, nickname: str) -> ReplyKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    b1 = InlineKeyboardButton(text='👍', callback_data='like'+id_match+' '+nickname)
    b2 = InlineKeyboardButton(text='👎', callback_data='disl'+id_match+' '+nickname)

    builder.row(b1, b2)

    return builder.as_markup()
