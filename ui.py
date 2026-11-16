from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Поиск на всех сайтах", callback_data="Wikipedia, Github и Stackoverflow")],
            [InlineKeyboardButton(text="Поиск на Wikipedia", callback_data="Wikipedia")],
            [InlineKeyboardButton(text="Поиск на Github", callback_data="Github")],
            [InlineKeyboardButton(text="Поиск на Stackoverflow", callback_data="Stackoverflow")],
        ]
    )

back_to_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
        ]
)