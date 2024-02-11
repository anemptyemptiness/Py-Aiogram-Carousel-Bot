from typing import Union
from datetime import datetime, timezone, timedelta

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, InputMediaPhoto, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from fsm.fsm import FSMStartShift
from keyboards.keyboards import create_cancel_kb, create_places_kb, create_yes_no_kb, create_agree_kb
from middlewares.album_middleware import AlbumsMiddleware
from config.config import config, place_chat
from lexicon.lexicon_ru import LEXICON_RU, rules
from db import DB


router_start_shift = Router()
router_start_shift.message.middleware(middleware=AlbumsMiddleware(2))


async def report(report_dict: dict, date: str, user_id: Union[int, str]) -> str:
    return f"📝Открытие смены\n\n" \
           f"Дата: {date}\n" \
           f"Точка: {report_dict['place']}\n" \
           f"Имя: {DB.get_current_name(user_id)}\n\n" \
           f"Есть ли дефекты: <em>{report_dict['is_defects']}</em>\n" \
           f"Чистая ли карусель: <em>{report_dict['is_clear']}</em>\n" \
           f"Включен ли свет: <em>{report_dict['is_light']}</em>\n" \
           f"Играет ли музыка: <em>{report_dict['is_music']}</em>\n" \
           f"Есть ли скрип: <em>{report_dict['is_scream']}</em>\n"


@router_start_shift.message(Command(commands="start_shift"), StateFilter(default_state))
async def process_start_shift_command(message: Message, state: FSMContext):
    await state.set_state(FSMStartShift.place)
    await message.answer(
        text="Пожалуйста, выберите рабочую точку",
        reply_markup=await create_places_kb(),
    )


@router_start_shift.callback_query(StateFilter(FSMStartShift.place), F.data == "place_novaya_riga")
async def process_place_1_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(place="Новая Рига")
    await callback.message.answer(
        text=f"{rules}",
        reply_markup=await create_agree_kb(),
    )
    await callback.answer(text="Рабочая точка успешно записана")
    await state.set_state(FSMStartShift.rules)


@router_start_shift.callback_query(StateFilter(FSMStartShift.place), F.data == "place_belaya_dacha")
async def process_place_2_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(place="Белая Дача")
    await callback.message.answer(
        text=f"{rules}",
        reply_markup=await create_agree_kb(),
    )
    await callback.answer(text="Рабочая точка успешно записана")
    await state.set_state(FSMStartShift.rules)


@router_start_shift.callback_query(StateFilter(FSMStartShift.place), F.data == "place_vnukovo")
async def process_place_3_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(place="Внуково")
    await callback.message.answer(
        text=f"{rules}",
        reply_markup=await create_agree_kb(),
    )
    await callback.answer(text="Рабочая точка успешно записана")
    await state.set_state(FSMStartShift.rules)


@router_start_shift.callback_query(StateFilter(FSMStartShift.place), F.data == "place_salaris")
async def process_place_4_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(place="Саларис")
    await callback.message.answer(
        text=f"{rules}",
        reply_markup=await create_agree_kb(),
    )
    await callback.answer(text="Рабочая точка успешно записана")
    await state.set_state(FSMStartShift.rules)


@router_start_shift.callback_query(StateFilter(FSMStartShift.place), F.data == "cancel")
async def process_place_cancel_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer(text="✅")
    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.place))
async def warning_start_shift_command(message: Message):
    await message.answer(
        text="Пожалуйста, выберите рабочую точку из списка выше",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.callback_query(StateFilter(FSMStartShift.rules), F.data == "agree")
async def process_rules_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Пожалуйста, сфотографируйте себя\n"
             "(соответственно, 1 фото)",
        reply_markup=await create_cancel_kb(),
    )
    await callback.answer(text="✅")
    await state.set_state(FSMStartShift.my_photo)


@router_start_shift.callback_query(StateFilter(FSMStartShift.rules), F.data == "cancel")
async def process_rules_cancel_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer(text="✅")
    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.rules))
async def warning_rules_command(message: Message):
    await message.answer(
        text="Нажмите на кнопку выше под сообщением пользовательского соглашения!",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.message(StateFilter(FSMStartShift.my_photo), F.photo)
async def process_my_photo_command(message: Message, state: FSMContext):
    await state.update_data(my_photo=message.photo[-1].file_id)
    await message.answer(
        text="Пожалуйста, сфотографируйте объект (1 фото)",
        reply_markup=await create_cancel_kb(),
    )
    await state.set_state(FSMStartShift.object_photo)


@router_start_shift.message(StateFilter(FSMStartShift.my_photo))
async def warning_my_photo_command(message: Message):
    await message.answer(
        text="Нужно отправить всего одно фото себя",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.message(StateFilter(FSMStartShift.object_photo), F.photo)
async def process_object_photo_command(message: Message, state: FSMContext):
    if "object_photo" not in await state.get_data():
        await state.update_data(object_photo=[message.photo[-1].file_id])

    await message.answer(
        text="Есть ли видимые дефекты?",
        reply_markup=await create_yes_no_kb(),
    )
    await state.set_state(FSMStartShift.is_defects)


@router_start_shift.message(StateFilter(FSMStartShift.object_photo))
async def warning_object_photo_command(message: Message):
    await message.answer(
        text="Нужно фото объекта",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_defects), F.data == "yes")
async def process_defects_yes_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_defects="yes")
    await callback.message.answer(
        text="Пожалуйста, сделайте фотографии дефектов (не более 10)",
        reply_markup=await create_cancel_kb(),
    )
    await callback.answer(text="✅")
    await state.set_state(FSMStartShift.defects_photo)


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_defects), F.data == "no")
async def process_defects_no_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_defects="no")
    await callback.message.answer(
        text="Карусель чистая?",
        reply_markup=await create_yes_no_kb(),
    )
    await callback.answer(text="✅")
    await state.set_state(FSMStartShift.is_clear)


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_defects), F.data == "cancel")
async def process_defects_cancel_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer(text="✅")
    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.is_defects))
async def warning_defects_command(message: Message):
    await message.answer(
        text="Нажмите на нужную кнопку выше",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.message(StateFilter(FSMStartShift.defects_photo), F.photo)
async def process_defects_photo_command(message: Message, state: FSMContext):
    if "defects_photo" not in await state.get_data():
        await state.update_data(defects_photo=[message.photo[-1].file_id])

    await message.answer(
        text="Карусель чистая?",
        reply_markup=await create_yes_no_kb(),
    )
    await state.set_state(FSMStartShift.is_clear)


@router_start_shift.message(StateFilter(FSMStartShift.defects_photo))
async def warning_defects_photo_command(message: Message):
    await message.answer(
        text="Нужно прислать фото дефектов (не более 10)",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_clear), F.data == "yes")
async def process_clear_yes_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_clear="yes")
    await callback.message.answer(
        text="Горит ли на ней свет?",
        reply_markup=await create_yes_no_kb(),
    )
    await callback.answer(text="✅")
    await state.set_state(FSMStartShift.is_light)


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_clear), F.data == "no")
async def process_clear_no_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_clear="no")
    await callback.message.answer(
        text="Горит ли на ней свет?",
        reply_markup=await create_yes_no_kb(),
    )
    await callback.answer(text="✅")
    await state.update_data(FSMStartShift.is_light)


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_clear), F.data == "cancel")
async def process_clear_cancel_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer(text="✅")
    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.is_clear))
async def warning_clear_command(message: Message):
    await message.answer(
        text="Нажмите на нужную кнопку выше",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_light), F.data == "yes")
async def process_light_yes_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_light="yes")
    await callback.message.answer(
        text="Включена ли музыка?",
        reply_markup=await create_yes_no_kb(),
    )
    await callback.answer(text="✅")
    await state.set_state(FSMStartShift.is_music)


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_light), F.data == "no")
async def process_light_no_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_light="no")
    await callback.message.answer(
        text="Включена ли музыка?",
        reply_markup=await create_yes_no_kb(),
    )
    await callback.answer(text="✅")
    await state.set_state(FSMStartShift.is_music)


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_light), F.data == "cancel")
async def process_light_cancel_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer(text="✅")
    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.is_light))
async def warning_light_command(message: Message):
    await message.answer(
        text="Нажмите на нужную кнопку выше",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_music), F.data == "yes")
async def process_music_yes_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_music="yes")
    await callback.message.answer(
        text="При запуске скрипит?",
        reply_markup=await create_yes_no_kb(),
    )
    await callback.answer(text="✅")
    await state.set_state(FSMStartShift.is_scream)


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_music), F.data == "no")
async def process_music_no_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_music="no")
    await callback.message.answer(
        text="При запуске скрипит?",
        reply_markup=await create_yes_no_kb(),
    )
    await callback.answer(text="✅")
    await state.set_state(FSMStartShift.is_scream)


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_music), F.data == "cancel")
async def process_music_cancel_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer(text="✅")
    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.is_music))
async def warning_music_command(message: Message):
    await message.answer(
        text="Нажмите на нужную кнопку выше",
        reply_markup=await create_cancel_kb(),
    )


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_scream), F.data == "yes")
async def process_scream_yes_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_scream="yes")

    try:
        start_shift_dict = await state.get_data()

        day_of_week = datetime.now(tz=timezone(timedelta(hours=3.0))).strftime('%A')
        current_date = datetime.now(tz=timezone(timedelta(hours=3.0))).strftime(f'%d/%m/%Y - {LEXICON_RU[day_of_week]}')

        object_photos = [InputMediaPhoto(
            media=photo_file_id,
            caption="Фото объекта" if i == 0 else ""
        ) for i, photo_file_id in enumerate(start_shift_dict['object_photo'])]

        await callback.message.bot.send_message(
            chat_id=place_chat[start_shift_dict['place']],
            text=await report(start_shift_dict, current_date, callback.message.chat.id),
            parse_mode="html",
        )

        await callback.message.bot.send_photo(
            chat_id=place_chat[start_shift_dict['place']],
            photo=start_shift_dict['my_photo'],
            caption='Фото сотрудника',
        )

        await callback.message.bot.send_media_group(
            chat_id=place_chat[start_shift_dict['place']],
            media=object_photos,
        )

        if "defects_photo" in start_shift_dict:
            defects_photo = [InputMediaPhoto(
                media=photo_file_id,
                caption="Фото дефектов" if i == 0 else ""
            ) for i, photo_file_id in enumerate(start_shift_dict['defects_photo'])]

            await callback.message.bot.send_media_group(
                chat_id=place_chat[start_shift_dict['place']],
                media=defects_photo,
            )

        await callback.message.answer(
            text="Данные успешно записаны!\n"
                 "Передаю отчёт руководству...",
            reply_markup=ReplyKeyboardRemove(),
        )

        await callback.message.answer(
            text="Вы вернулись в главное меню",
        )

        await callback.answer(text="✅")

    except Exception as e:
        await callback.message.answer(
            text="Упс... что-то пошло не так, сообщите руководству!",
            reply_markup=ReplyKeyboardRemove(),
        )

        await callback.message.answer(
            text="Вы вернулись в главное меню",
        )

        await callback.message.bot.send_message(
            chat_id=config.admins[0],
            text=f"Start shift report error:\n\n{e}",
            reply_markup=ReplyKeyboardRemove(),
        )
    finally:
        await state.clear()


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_scream), F.data == "no")
async def process_scream_no_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_scream="no")

    try:
        start_shift_dict = await state.get_data()

        day_of_week = datetime.now(tz=timezone(timedelta(hours=3.0))).strftime('%A')
        current_date = datetime.now(tz=timezone(timedelta(hours=3.0))).strftime(f'%d/%m/%Y - {LEXICON_RU[day_of_week]}')

        object_photos = [InputMediaPhoto(
            media=photo_file_id,
            caption="Фото объекта" if i == 0 else ""
        ) for i, photo_file_id in enumerate(start_shift_dict['object_photo'])]

        await callback.message.bot.send_message(
            chat_id=place_chat[start_shift_dict['place']],
            text=await report(start_shift_dict, current_date, callback.message.chat.id),
            parse_mode="html",
        )

        await callback.message.bot.send_photo(
            chat_id=place_chat[start_shift_dict['place']],
            photo=start_shift_dict['my_photo'],
            caption='Фото сотрудника',
        )

        await callback.message.bot.send_media_group(
            chat_id=place_chat[start_shift_dict['place']],
            media=object_photos,
        )

        if "defects_photo" in start_shift_dict:
            defects_photo = [InputMediaPhoto(
                media=photo_file_id,
                caption="Фото дефектов" if i == 0 else ""
            ) for i, photo_file_id in enumerate(start_shift_dict['defects_photo'])]

            await callback.message.bot.send_media_group(
                chat_id=place_chat[start_shift_dict['place']],
                media=defects_photo,
            )

        await callback.message.answer(
            text="Данные успешно записаны!\n"
                 "Передаю отчёт руководству...",
            reply_markup=ReplyKeyboardRemove(),
        )

        await callback.message.answer(
            text="Вы вернулись в главное меню",
        )

        await callback.answer(text="✅")

    except Exception as e:
        await callback.message.answer(
            text="Упс... что-то пошло не так, сообщите руководству!",
            reply_markup=ReplyKeyboardRemove(),
        )

        await callback.message.answer(
            text="Вы вернулись в главное меню",
        )

        await callback.message.bot.send_message(
            chat_id=config.admins[0],
            text=f"Start shift report error:\n\n{e}",
            reply_markup=ReplyKeyboardRemove(),
        )
    finally:
        await state.clear()


@router_start_shift.callback_query(StateFilter(FSMStartShift.is_scream), F.data == "cancel")
async def process_scream_cancel_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer(text="✅")
    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.is_scream))
async def warning_scream_command(message: Message):
    await message.answer(
        text="Нажмите на нужную кнопку выше",
        reply_markup=await create_cancel_kb(),
    )
