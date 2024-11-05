from aiogram.fsm.state import State, StatesGroup


class ChangePromo(StatesGroup):
    insert_promo = State()


class MakeSpam(StatesGroup):
    insert_spam_message = State()
    check_spam_message = State()


class AddAdmin(StatesGroup):
    insert_admin_id = State()
    add_admin = State()


class CheckUnSub(StatesGroup):
    insert_feedback = State()


class JoinToContest(StatesGroup):
    insert_photo = State()
