from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_buttons = [
    [
        InlineKeyboardButton(text='Получить скидку 💸', callback_data='get_promo')
    ],
    [
        InlineKeyboardButton(text='Участвовать в конкурсе 🏆', callback_data='join_contest')
    ],
    [
        InlineKeyboardButton(text='Связаться с менеджером 📱', url="https://t.me/mdim66", callback_data='contact')
    ]
]

start_keyboard = InlineKeyboardMarkup(inline_keyboard=start_buttons)


check_follow_button = InlineKeyboardBuilder()
check_follow_button.add(InlineKeyboardButton(text='Проверить подписку', callback_data='check_follow'))

admin_buttons = [
    [
        InlineKeyboardButton(text='Изменить промокод', callback_data='change_promo'),
        InlineKeyboardButton(text='Сделать рассылку', callback_data='make_spam'),
    ],
    [
        InlineKeyboardButton(text='Показать фидбэк', callback_data='show_feedback'),
        InlineKeyboardButton(text='Статистика', callback_data='stats')
    ]
]

admin_panel_keyboard = InlineKeyboardMarkup(inline_keyboard=admin_buttons)

yes_or_no_keyboard = InlineKeyboardBuilder()
yes_or_no_keyboard.add(InlineKeyboardButton(text='Да', callback_data='yes'),
                       InlineKeyboardButton(text='Нет', callback_data='no'))
