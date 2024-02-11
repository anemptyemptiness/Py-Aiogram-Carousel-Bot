from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup


async def create_yes_no_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Да",
                              callback_data="yes"),
         InlineKeyboardButton(text="Нет",
                              callback_data="no")],
        [InlineKeyboardButton(text="Отмена",
                              callback_data="cancel")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


async def create_cancel_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Отмена")]
    ]

    return ReplyKeyboardMarkup(keyboard=kb,
                               resize_keyboard=True)


async def create_places_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(
            text="Новая Рига",
            callback_data="place_novaya_riga",
        )],
        [InlineKeyboardButton(
            text="Белая Дача",
            callback_data="place_belaya_dacha",
        )],
        [InlineKeyboardButton(
            text="Внуково",
            callback_data="place_vnukovo",
        )],
        [InlineKeyboardButton(
            text="Саларис",
            callback_data="place_salaris",
        )],
        [InlineKeyboardButton(
            text="Отмена",
            callback_data="cancel"
        )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


async def create_agree_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(
            text="Согласен",
            callback_data="agree")],
        [InlineKeyboardButton(
            text="Отмена",
            callback_data="cancel"
        )]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


async def create_admin_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(
            text="Статистика за последнюю неделю",
            callback_data="last_week",
        )],
        [InlineKeyboardButton(
            text="Статистика за последний месяц",
            callback_data="last_month",
        )],
        [InlineKeyboardButton(
            text="Статистика за последний год",
            callback_data="last_year",
        )],
        [InlineKeyboardButton(
            text="Задать вручную",
            callback_data="by_hand",
        )],
        [InlineKeyboardButton(
            text="Выход",
            callback_data="exit",
        )],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)
