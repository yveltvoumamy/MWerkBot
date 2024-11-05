import os

from aiogram import Bot, Dispatcher, html, F
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, CallbackQuery

from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.handler.sates_group import *
from src.handler.keyboards import *
from src.data.data_base import *
from src.data.google_drive import *

import logging
import sys

bot = Bot(token=get_attr_from_csv('config', 'token'))
dp = Dispatcher()

'''
USER PANEL
'''

daily_counter_start_members = 0
daily_counter_subscribe_members = 0
daily_counter_feedback_messages = 0
daily_counter_unsub_members = 0


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(true_check_unsub, 'interval', seconds=60)
    scheduler.add_job(new_day_poling, 'interval', seconds=24 * 60 * 60)
    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def new_day_poling():
    global daily_counter_subscribe_members, daily_counter_feedback_messages, daily_counter_start_members, daily_counter_unsub_members
    '''
    await bot.send_message(chat_id=100940188, text=f'Сегодня {daily_counter_start_members} человек впервые запустили бота\n'
                                              f'И {daily_counter_subscribe_members} получили промокод за подписку\n'
                                              f'А {daily_counter_unsub_members} отписались от канала')
    '''
    await bot.send_message(chat_id=100940188, text=f'Сегодня {daily_counter_start_members} человек впервые запустили бота\n'
                                                   f'И {daily_counter_subscribe_members} получили промокод за подписку\n'
                                                   f'А {daily_counter_unsub_members} отписались от канала\n'
                                                   f'Так же у нас {daily_counter_feedback_messages} новых отзывов')
    daily_counter_start_members = 0
    daily_counter_subscribe_members = 0
    daily_counter_feedback_messages = 0
    daily_counter_unsub_members = 0


@dp.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext) -> None:
    global daily_counter_start_members, daily_counter_subscribe_members
    if await add_id_to_csv('users_id', message.from_user.id, 'unsub'):
        daily_counter_start_members += 1
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!\n"
                         f"Я бот компании Melnichuk Werk. Благодарю Вас за покупку нашего товара.\n\n"
                         f"Подпишитесь на наш телеграмм-канал\nhttps://t.me/melnichuk_werk"
                         f" и я пришлю Вам в подарок промокод на скидку 40%.", parse_mode='HTML')
    await send_menu(message)


@dp.message(Command('menu'))
async def send_menu(message: Message) -> None:
    await message.answer(f'ᅠ ᅠ ', reply_markup=start_keyboard)


@dp.callback_query(F.data == 'get_promo')
async def get_promo(callback_query: CallbackQuery) -> None:
    await callback_query.answer(f'')
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id)
    message = callback_query.message
    chat_member = await bot.get_chat_member(chat_id='-1002140764634', user_id=message.chat.id)
    if chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator':
        PROMO = get_attr_from_csv('config', 'promo')
        df = pd.read_csv(Path('src', 'data', 'users_id.csv'))
        if df.loc[df['id'] == message.chat.id, 'status'].values[0] == 'unsub':
            daily_counter_subscribe_members += 1
        df.loc[df['id'] == message.chat.id, 'status'] = 'sub'
        df.to_csv(Path('src', 'data', 'users_id.csv'), index=False)
        await (message.answer(f'Супер, вы уже подписаны на наш канал !\nВот ваш промокод `{PROMO}\n\n`'
                              f'Он дает скидку 40% на один заказ в нашем магазине на Озон\n'
                              f' https://www.ozon.ru/seller/melnichuk-werk-1005470/products/\n\n'
                              f'Количество товара в заказе не ограничено!',
                              parse_mode=ParseMode.MARKDOWN))
    else:
        await message.answer(
            f'К сожалению, вы не подписаны :(\nПодпишитесь на канал https://t.me/melnichuk_werk и нажмите на кнопку',
            reply_markup=check_follow_button.as_markup())


@dp.message(Command('help'))
async def process_help_command(message: Message) -> None:
    if await check_admin_status(message):
        await message.answer(f'/start - команда для начала работы с ботом и проверки подписки\n'
                             f'/exit - команда для завершения всех процессов внутри бота (на случай, если кнопки залагают)\n'
                             f'/admin - команда для входа в админ панель\n'
                             f'В админ панели есть 3 фунции: \n'
                             f'Изменить промокод (который отправляется пользователям при подписке)\n'
                             f'Сделать рассылку (всем пользователям хоть раз писавшим боту)\n'
                             f'Показать фидбэк (отзывы людей, отписавшихся от канала)\n'
                             f'# могу сделать команду /check_sub которая будет то же самое что /start, но без приветствия\n'
                             f'# при обновлении промокода стоит делать рассылку пользователям, что их промокод не работает и вот держите новый. '
                             f'Я могу сделать это автоматизировано, либо можете делать это вручную через рассылку админа')
    else:
        await message.answer(f'/start - команда для начала работы с ботом и проверки подписки\n'
                             f'/exit - команда для завершения всех процессов внутри бота (на случай, если кнопки залагают)\n')


@dp.message(CheckUnSub.insert_feedback)
async def insert_feedback_unsub(message: Message, state: FSMContext) -> None:
    global daily_counter_feedback_messages
    new_feedback = message.text
    with open(Path('src', 'data', 'feedback.txt'), 'r') as file:
        feedback_data = ''.join(file.readlines())
    if message.from_user.username is not None:
        feedback_data = f'{message.from_user.full_name} (@{message.from_user.username}): {new_feedback} \n{feedback_data}'
    else:
        feedback_data = f'{message.from_user.full_name} (@{message.from_user.id}): {new_feedback} \n{feedback_data}'
    with open(Path('src', 'data', 'feedback.txt'), 'w') as file:
        file.write(feedback_data)
    daily_counter_feedback_messages += 1
    await message.answer(f'Спасибо за оставленный отзыв !\n'
                         f'В ближайшее время мы его обработаем и постараемся сделать работу над ошибками\n'
                         f'На всякий случай оставим ссылку, чтобы вы смогли через время зайти и убедиться,'
                         f' что мы прислушались к вашему мнению\n'
                         f'https://t.me/melnichuk_werk'
                         )
    await state.clear()
    await asyncio.sleep(14 * 60 * 60 * 24)  # * 60 * 60 * 24
    await message.answer(f'Мы сделали работу над ошибками, самое время зайти и проверить !\n'
                         f'https://t.me/melnichuk_werk')


@dp.callback_query(F.data == "stats")
async def get_stats(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer('')
    global daily_counter_feedback_messages, daily_counter_start_members, \
        daily_counter_unsub_members, daily_counter_subscribe_members
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=f'Сегодня {daily_counter_start_members} человек впервые запустили бота\n'
                                f'И {daily_counter_subscribe_members} получили промокод за подписку\n'
                                f'А {daily_counter_unsub_members} отписались от канала\n'
                                f'Так же у нас {daily_counter_feedback_messages} новых отзывов')


@dp.callback_query(F.data == "check_follow")
async def check_follow(callback_query: CallbackQuery, state: FSMContext) -> None:
    global daily_counter_subscribe_members
    await callback_query.answer(f'')
    chat_member = await bot.get_chat_member(chat_id='-1002140764634', user_id=callback_query.message.chat.id)

    if chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator':
        PROMO = get_attr_from_csv('config', 'promo')
        df = pd.read_csv(Path('src', 'data', 'users_id.csv'))
        if df.loc[df['id'] == callback_query.message.chat.id, 'status'].values[0] == 'unsub':
            daily_counter_subscribe_members += 1
        df.loc[df['id'] == callback_query.message.chat.id, 'status'] = 'sub'
        df.to_csv(Path('src', 'data', 'users_id.csv'), index=False)
        await (callback_query.message.answer(f'Ура! Вы теперь с нами!)\n '
                                             f'Вот ваш промокод `{PROMO}`\n\n'
                                             f'Он дает скидку 40% на один заказ в нашем магазине на Озон\n'
                                             f'https://www.ozon.ru/seller/melnichuk-werk-1005470/products/\n\n'
                                             f'Количество товара в заказе не ограничено!',
                                             parse_mode=ParseMode.MARKDOWN))
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id)
        await asyncio.sleep(60 * 60 * 15)
        await callback_query.message.answer(f'Если у Вас есть отзывы и пожелания по нашему товару, или Вы хотите сделать'
                                            f' индивидуальный заказ - пишите @mdim66.\n\n'
                                            f'Мы производим товары для Вас, поэтому обратная связь очень важна. Пишите, '
                                            f'не стесняйтесь, будем благодарны за любые отзывы, особенно негативные) '
                                            f'потому что качество для нас важнее всего!)')
    else:
        await callback_query.message.answer(
            f'К сожалению, вы не подписаны :(\nПодпишитесь на канал t.me/melnichuk_werk и нажмите на кнопку',
            reply_markup=check_follow_button.as_markup())
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id)


async def true_check_unsub():
    df = pd.read_csv(Path('src', 'data','users_id.csv'))
    tasks = [update_member_status(row, df) for index, row in df.iterrows()]
    await asyncio.gather(*tasks)
    df.to_csv(Path('src', 'data','users_id.csv'), index=False)


async def update_member_status(row, df):
    global daily_counter_unsub_members
    user_id = row['id']

    state_with: FSMContext = FSMContext(storage=dp.storage,
        key=StorageKey(chat_id=user_id, user_id=user_id, bot_id=bot.id))

    current_status = row['status']
    new_status = await check_member_status(user_id)
    df.loc[df['id'] == user_id, 'status'] = new_status
    df.to_csv(Path('src', 'data','users_id.csv'), index=False)
    if current_status == 'sub' and new_status == 'unsub':
        daily_counter_unsub_members += 1
        await bot.send_message(user_id, f'Расскажите, пожалуйста, почему Вы отписались от нашего канала?\n\n'
                                        f'Нам очень важна Ваша обратная связь.')
        await state_with.set_state(CheckUnSub.insert_feedback)


async def check_member_status(user_id) -> str:
    chat_member = await bot.get_chat_member(chat_id='-1002140764634', user_id=user_id)
    if not (chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator'):
        return 'unsub'
    return 'sub'
'''
ADMIN PANEL
'''


async def check_admin_status(message: Message) -> bool:
    current_id = message.chat.id
    if current_id in convert_csv_id_to_array('admin_list'):
        return True
    else:
        await message.answer(f'К сожалению, у вас нет права доступа к admin панели :(')
        return False


@dp.message(Command('admin'))
async def open_admin_panel(message: Message) -> None:
    if await check_admin_status(message):
        await message.answer(f'Поздравляю, вы вошли в admin панель !\nНиже перечислены все возможные функции',
                             reply_markup=admin_panel_keyboard)
    else:
        return


@dp.message(Command('exit'))
async def exit_from_state(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer(f'Вы завершили все текущие процедуры')


@dp.callback_query(F.data == 'change_promo')
async def change_promo(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not await check_admin_status(callback_query.message):
        return
    await state.set_state(ChangePromo.insert_promo)
    PROMO = get_attr_from_csv('config', 'promo')
    await callback_query.message.answer(f'Текущий промокод - `{PROMO}`\nВведите новый промокод', parse_mode=ParseMode.MARKDOWN)
    await callback_query.answer('')


@dp.message(ChangePromo.insert_promo)
async def insert_promo(message: Message, state: FSMContext) -> None:
    if not await check_admin_status(message):
        return
    await set_attr_from_csv('config', 'promo', message.text)
    PROMO = get_attr_from_csv('config', 'promo')
    await message.answer(f'Отлично, новый промокод - `{PROMO}`', parse_mode=ParseMode.MARKDOWN)
    await state.clear()


@dp.callback_query(F.data == 'make_spam')
async def insert_spam_message(callback_query: CallbackQuery, state: FSMContext) -> None:
    if not await check_admin_status(callback_query.message):
        return
    await state.set_state(MakeSpam.insert_spam_message)
    await callback_query.message.answer('Введите сообщние, которое хотите отправить всем пользователям')
    await callback_query.answer('')


@dp.message(MakeSpam.insert_spam_message)
async def check_spam_message(message: Message, state: FSMContext) -> None:
    with open(Path('src', 'data', 'spam_message.txt'), 'w', encoding='utf-8') as file:
        file.write(message.text)
    await state.set_state(MakeSpam.check_spam_message)
    await message.answer(f'Все пользователи получат такое сообщение:')
    with open(Path('src', 'data', 'spam_message.txt'), 'r', encoding='utf-8') as file:
        spam_message = ''.join(file.readlines())
        print(spam_message)
        await bot.send_message(message.chat.id, spam_message)
    await message.answer('Вы проверили текст и хотите его отправить ?',
                         reply_markup=yes_or_no_keyboard.as_markup())


@dp.callback_query(F.data == 'yes')
@dp.message(MakeSpam.check_spam_message)
async def send_spam_to_users(callback_query: CallbackQuery, state: FSMContext) -> None:
    spam_message = ''
    with open(Path('src', 'data', 'spam_message.txt'), 'r', encoding='utf-8') as file:
        spam_message = spam_message.join(file.readlines())
    await callback_query.message.answer(f'Каждому пользователю было отправлено сообщение:')
    await bot.send_message(callback_query.message.chat.id, spam_message)
    for user_id in convert_csv_id_to_array('users_id'):
        await bot.send_message(chat_id=str(int(user_id)), text=spam_message)
        await callback_query.message.answer(f'пользователю {user_id} было отправлено сообщение: {spam_message}')
    await callback_query.answer('')
    await state.clear()
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id)


@dp.callback_query(F.data == 'no')
@dp.message(MakeSpam.check_spam_message)
async def cancel_spam_message(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer('Отправка сообщения успешно отменена')
    await callback_query.answer('')
    await state.clear()
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id)


@dp.callback_query(F.data == 'show_feedback')
async def show_feedback(callback_query: CallbackQuery, state: FSMContext) -> None:
    with open(Path('src', 'data', 'feedback.txt'), 'r') as file:
        await callback_query.message.answer(''.join(file.readlines()))
    await callback_query.answer('')


@dp.callback_query(F.data == 'contact')
async def send_contact(callback_query: CallbackQuery) -> None:
    message = callback_query.message
    await callback_query.answer('')
    await message.answer('@mdim66')


@dp.callback_query(F.data == 'join_contest')
async def join_to_contest(callback_query: CallbackQuery, state: FSMContext) -> None:
    message = callback_query.message
    await callback_query.answer('')
    await message.answer('Чтобы принять участие в конкурсе на самую высокую башню из кубиков, '
                         'отправьте скриншот (фото, не документ) отзыва с вашей башней')
    await state.set_state(JoinToContest.insert_photo)


@dp.message(JoinToContest.insert_photo)
async def taking_photo(message: Message, state: FSMContext) -> None:
    if message.content_type != 'photo':
        await message.reply(f'Это не фото, а {message.content_type}, '
                            f'отправьте фото, пожалуйста, чтобы выйти напишите /exit')
        return
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    if message.from_user.username is not None:
        file_name = f'@{message.from_user.username}'
    else:
        file_name = f'@{message.from_user.id}'
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Составляем полный путь к файлу test.txt
    file_path = os.path.abspath(os.path.join(current_directory, '..', '..', file_name))

    # print(f'Полный путь к файлу test.txt: {file_path}')
    # Загрузить файл
    await message.answer(f'сохраняю ващ файл в директорию {file_path}')
    await bot.download_file(file.file_path, file_name)
    await message.answer(f'отправили ваше фото на загрузку, подождите, пожалуйста')
    if upload_photo_to_gdrive(file_name, file_path):
        await message.answer(f'Фото успешно загружено, теперь вы участнкик конкурса !')
    else:
        await message.answer('Не удалось загрузить фото из-за ошибки на сервере, приносим свои извинения,'
                             ' попробуйте еще раз позже')
        await bot.send_message(chat_id=100940188, text='У пользователя не получилось загрузить'
                                                       ' фото на конкурс из-за ошибки кода')
    os.remove(file_path)

    await state.clear()


'''
ADD_ADMIN_BUTTON

@dp.callback_query(F.data == 'add_admin')
async def add_admin(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer('Введите id пользователя, котрого хотите добавить в администраторы\n'
                                        'id можно узнать переслав сообщение пользователя в бота https://t.me/getmyid_bot')
    await state.set_state(AddAdmin.insert_admin_id)


@dp.message(AddAdmin.insert_admin_id)
async def check_correct_id(message: Message, state: FSMContext) -> None:
    try:
        user = bot.get_chat(int(message.text))
        await message.answer(f'Вы уверены, что хотите добавить пользователя'
                             f' {html.bold(user.full_name)}', reply_markup=yes_or_no_keyboard.as_markup())
        await state.set_state(AddAdmin.add_admin)
        with open(Path('src', 'data', 'tmp.txt'), 'w') as file:
            file.write(message.text)
    except:
        await message.answer(f'Произошла ошибка, скорее всего вы ввели некорректный id, введите id еще раз')


@dp.message(AddAdmin.add_admin)
@dp.callback_query(F.data == 'yes')
async def add_admin(callback_query: CallbackQuery, state: FSMContext) -> None:
    with open(Path('src', 'data', 'tmp.txt'), 'r') as file:
        new_admin = ''.join(file.readlines())
    await set_attr_from_csv('admin_list', 'id', new_admin)
    user = bot.get_chat(int(new_admin))
    await callback_query.message.answer(f'Пользователь {html.bold(user.full_name)}'
                                        f' успешно добавлен в список администраторов')
    await callback_query.answer('')
    await state.clear()
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id)


@dp.message(AddAdmin.add_admin)
@dp.callback_query(F.data == 'no')
async def cancel_add_admin(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer('Добавление нового администратора успешно отменено')
    await callback_query.answer('')
    await state.clear()
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id)

'''

