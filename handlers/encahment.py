from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, InputMediaPhoto, CallbackQuery
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from config.config import config
from fsm.fsm import FSMEncashment
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import create_cancel_kb, create_places_kb
from middlewares.album_middleware import AlbumsMiddleware
from config.config import place_chat


router_encashment = Router()
router_encashment.message.middleware(middleware=AlbumsMiddleware(2))


async def report(dictionary: dict, date):
    return "📝Инкассация:\n\n" \
           f"Точка: {dictionary['place']}\n" \
           f"Дата: {date}\n\n" \
           f"Кто инкассировал: <em>{dictionary['who']}</em>\n" \
           f"Дата инкассации: <em>{dictionary['date']}</em>\n" \
           f"Сумма инкассации: <em>{dictionary['summary']}</em>"


@router_encashment.message(Command(commands="encashment"), StateFilter(default_state))
async def process_place_command(message: Message, state: FSMContext):
    await state.set_state(FSMEncashment.place)
    await message.answer(
        text="Выберите точку, на которой Вы сейчас находитесь",
        reply_markup=await create_places_kb(),
    )


@router_encashment.callback_query(StateFilter(FSMEncashment.place), F.data == "place_novaya_riga")
async def process_place_1_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(place="Новая Рига")
    await callback.message.answer(
        text="Кто инкассировал?",
        reply_markup=await create_cancel_kb(),
    )
    await callback.answer(text="Рабочая точка успешно записана")
    await state.set_state(FSMEncashment.who)


@router_encashment.callback_query(StateFilter(FSMEncashment.place), F.data == "place_belaya_dacha")
async def process_place_2_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(place="Белая Дача")
    await callback.message.answer(
        text="Кто инкассировал?",
        reply_markup=await create_cancel_kb(),
    )
    await callback.answer(text="Рабочая точка успешно записана")
    await state.set_state(FSMEncashment.who)


@router_encashment.callback_query(StateFilter(FSMEncashment.place), F.data == "place_vnukovo")
async def process_place_3_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(place="Внуково")
    await callback.message.answer(
        text="Кто инкассировал?",
        reply_markup=await create_cancel_kb(),
    )
    await callback.answer(text="Рабочая точка успешно записана")
    await state.set_state(FSMEncashment.who)


@router_encashment.callback_query(StateFilter(FSMEncashment.place), F.data == "place_salaris")
async def process_place_4_command(callback: CallbackQuery, state: FSMContext):
    await state.update_data(place="Саларис")
    await callback.message.answer(
        text="Кто инкассировал?",
        reply_markup=await create_cancel_kb(),
    )
    await callback.answer(text="Рабочая точка успешно записана")
    await state.set_state(FSMEncashment.who)


@router_encashment.callback_query(StateFilter(FSMEncashment.place), F.data == "cancel")
async def process_place_cancel_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer(text="✅")
    await state.clear()


@router_encashment.message(StateFilter(FSMEncashment.place))
async def warning_place_command(message: Message):
    await message.answer(
        text="Выберите рабочую точку ниже из выпадающего списка",
        reply_markup=await create_cancel_kb(),
    )


@router_encashment.message(StateFilter(FSMEncashment.who), F.text)
async def process_who_command(message: Message, state: FSMContext):
    await state.update_data(who=message.text)
    await message.answer(
        text="Напишите дату инкассации",
        reply_markup=await create_cancel_kb(),
    )
    await state.set_state(FSMEncashment.date)


@router_encashment.message(StateFilter(FSMEncashment.who))
async def warning_who_command(message: Message):
    await message.answer(
        text="Напишите, кто инкассировал",
        reply_markup=await create_cancel_kb(),
    )


@router_encashment.message(StateFilter(FSMEncashment.date), F.text)
async def process_date_command(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer(
        text="Напишите сумму инкассации",
        reply_markup=await create_cancel_kb(),
    )
    await state.set_state(FSMEncashment.summary)


@router_encashment.message(StateFilter(FSMEncashment.date))
async def warning_date_command(message: Message):
    await message.answer(
        text="Напишите дату инкассации",
        reply_markup=await create_cancel_kb(),
    )


@router_encashment.message(StateFilter(FSMEncashment.summary), F.text)
async def process_summary_command(message: Message, state: FSMContext):
    await state.update_data(summary=message.text)
    await message.answer(
        text="Пришлите фото тетради с подписью отв. лица",
        reply_markup=await create_cancel_kb(),
    )
    await state.set_state(FSMEncashment.photos)


@router_encashment.message(StateFilter(FSMEncashment.summary))
async def warning_summary_command(message: Message):
    await message.answer(
        text="Напишите сумму инкассации",
        reply_markup=await create_cancel_kb(),
    )


@router_encashment.message(StateFilter(FSMEncashment.photos), F.photo)
async def process_photos_command(message: Message, state: FSMContext):
    if "photos" not in await state.get_data():
        await state.update_data(photos=[message.photo[-1].file_id])

    try:
        encashment_dict = await state.get_data()

        day_of_week = datetime.now(tz=timezone(timedelta(hours=3.0))).strftime('%A')
        date = datetime.now(tz=timezone(timedelta(hours=3.0))).strftime(f'%d/%m/%Y - {LEXICON_RU[day_of_week]}')

        await message.bot.send_message(
            chat_id=place_chat[encashment_dict['place']],
            text=await report(
                dictionary=encashment_dict,
                date=date
            ),
            parse_mode="html",
        )

        photos = [InputMediaPhoto(
            media=photo_file_id,
            caption="Фото тетради" if i == 0 else ""
        ) for i, photo_file_id in enumerate(encashment_dict['photos'])]

        await message.bot.send_media_group(
            media=photos,
            chat_id=place_chat[encashment_dict['place']],
        )

        await message.answer(
            text="Отлично! Формирую отчёт...\nОтправляю начальству!",
            reply_markup=ReplyKeyboardRemove(),
        )

        await message.answer(
            text="Вы вернулись в главное меню",
        )

    except Exception as e:
        await message.bot.send_message(
            text=f"Encashment report error: {e}\n"
                 f"User_id: {message.from_user.id}",
            chat_id=config.admins[0],
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer(
            text="Упс... что-то пошло не так, сообщите руководству!",
            reply_markup=ReplyKeyboardRemove(),
        )

    finally:
        await state.clear()


@router_encashment.message(StateFilter(FSMEncashment.photos))
async def warning_photos_command(message: Message):
    await message.answer(
        text="Пришлите фото тетради с подписью отв. лица",
        reply_markup=await create_cancel_kb(),
    )
