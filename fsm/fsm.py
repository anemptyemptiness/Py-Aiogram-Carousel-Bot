from aiogram.fsm.state import StatesGroup, State


class Authorise(StatesGroup):
    fullname = State()


class FSMStartShift(StatesGroup):
    place = State()
    rules = State()
    my_photo = State()
    object_photo = State()
    is_defects = State()
    defects_photo = State()
    is_clear = State()
    is_light = State()
    is_music = State()
    is_scream = State()


class FSMAttractionsCheck(StatesGroup):
    place = State()
    bill_acceptor = State()
    defects_on_bill_acceptor = State()
    attracts = State()
    defects_on_attracts = State()


class FSMFinishShift(StatesGroup):
    place = State()
    summary = State()
    beneficiaries = State()
    photo_of_beneficiaries = State()
    cash = State()
    online_cash = State()
    qr_code = State()
    expenditure = State()
    salary = State()
    convert = State()
    count_rentals_carous = State()
    count_cars_5 = State()
    count_cars_10 = State()
    count_rentals_cart = State()
    count_additional = State()
    necessary_photos = State()
    object_photo = State()


class FSMEncashment(StatesGroup):
    place = State()
    who = State()
    date = State()
    summary = State()
    photos = State()


class FSMAdmin(StatesGroup):
    stats = State()
    money = State()
    money_by_hand = State()
