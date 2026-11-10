import os, dotenv

dotenv.load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не удалось найти BOT_TOKEN")


import asyncio
import aiogram
from aiogram import F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

menu_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Поиск на всех сайтах", callback_data="all")],
            [InlineKeyboardButton(text="Поиск на Wikipedia", callback_data="wiki")],
            [InlineKeyboardButton(text="Поиск на Github", callback_data="git")],
            [InlineKeyboardButton(text="Поиск на Stackoverflow", callback_data="stack")],
        ]
    )

back_to_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
        ]
)


async def my_answer(callback: CallbackQuery):
    await callback.answer()

    if isinstance(callback.message, Message):
        await callback.message.answer("Введите тему для поиска или нажмите кнопку, чтобы вернутся в главное меню",
                                      reply_markup=back_to_menu, )
        await callback.message.delete()

    # Не определился, что лучше выглядит, удаление или изменение сообщения
    # await callback.answer()
    #
    # if isinstance(callback.message, Message):
    #     await callback.message.edit_text(
    #         "Введите тему для поиска или нажмите кнопку, чтобы вернутся в главное меню",
    #         reply_markup=back_to_menu,
    #     )

async def menu_handler(callback: CallbackQuery):
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer("Выберете сайт на котором хотите найти интересующую вас тему:",
                                       reply_markup=menu_keyboard, )
        await callback.message.delete()


async def all_search(callback: CallbackQuery):
    await my_answer(callback)






async def wiki_search(callback: CallbackQuery):
    await my_answer(callback)






async def git_search(callback: CallbackQuery):
    await my_answer(callback)





async def stack_search(callback: CallbackQuery):
    await my_answer(callback)





async def start_handler(message: Message):
    await message.answer("Приветствую!\n"
                         "Этот бот поможет вам найти статьи, на интересующие вас темы, на таких сайтах как:\n"
                         "Wikipedia, Github и Stackoverflow\n"
                         "Ниже выберете нужный сайт для поиска.", reply_markup=menu_keyboard,
                        )



async def main():
    bot = aiogram.Bot(token=BOT_TOKEN)
    dispatcher = aiogram.Dispatcher()


    dispatcher.message.register(start_handler, Command("start"))
    dispatcher.callback_query.register(all_search, F.data == "all")
    dispatcher.callback_query.register(wiki_search, F.data == "wiki")
    dispatcher.callback_query.register(git_search, F.data == "git")
    dispatcher.callback_query.register(stack_search, F.data == "stack")
    dispatcher.callback_query.register(menu_handler, F.data == "menu")

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())