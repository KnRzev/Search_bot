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
from aiogram.fsm.context import FSMContext

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

without_source = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Поиск везде", callback_data="all"),
            InlineKeyboardButton(text="Поиск на Wikipedia", callback_data="wiki")],
            [InlineKeyboardButton(text="Поиск на Github", callback_data="git"),
            InlineKeyboardButton(text="Поиск на Stackoverflow", callback_data="stack")],
            [InlineKeyboardButton(text="Главное меню", callback_data="menu")]
        ]
)


async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Приветствую!\n"
                         "Этот бот поможет вам найти статьи, на интересующие вас темы, на таких сайтах как:\n"
                         "Wikipedia, Github и Stackoverflow\n"
                         "Ниже выберете нужный сайт для поиска.", reply_markup=menu_keyboard,
                        )

async def menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.delete()
        await callback.message.answer("Выберете сайт на котором хотите найти интересующую вас тему:", reply_markup=menu_keyboard)



async def answer_before_search(event: CallbackQuery | Message, state: FSMContext):
    if isinstance(event, CallbackQuery):
        await event.answer()

        await state.update_data(source=event.data)

        if isinstance(event.message, Message):
            await event.message.delete()
            await event.message.answer("Введите тему для поиска или вернитесь в главное меню:", reply_markup=back_to_menu)

    elif isinstance(event, Message):
        data = await state.get_data()
        source = data.get("source")

        if source == "in_search":
            await event.delete()
            return

        if source is None:
            await event.delete()
            await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)
            await event.answer("Сначала выберите сайт для поиска или вернитесь в главное меню:", reply_markup=without_source)
            return

        search_func = {
            "all" : all_search,
            "wiki" : wiki_search,
            "git" : git_search,
            "stack" : stack_search,
        }

        func = search_func[source]
        query = event.text
        await state.update_data(source="in_search")
        await func(event, query, state)

        #print("Выбранный сайт:", source)
        #print("Введённый текст:", event.text)





async def all_search(event, query: str, state: FSMContext):
    await event.delete()
    await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)

    await event.answer(f"Ищу на всех сайтах по теме: {query}")

async def wiki_search(event, query: str, state: FSMContext):
    await event.delete()
    await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)

    await event.answer(f"Ищу статьи на Wikipedia по теме: {query}")

async def git_search(event, query: str, state: FSMContext):
    await event.delete()
    await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)

    await event.answer(f"Ищу репозитории и проекты на Github по теме: {query}")


async def stack_search(event, query: str, state: FSMContext):
    await event.delete()
    await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)

    await event.answer(f"Ищу похожие вопросы на Stackoverflow по теме: {query}")








async def main():
    bot = aiogram.Bot(token=BOT_TOKEN)
    dispatcher = aiogram.Dispatcher()

    dispatcher.message.register(start_handler, Command("start"))
    dispatcher.callback_query.register(menu_handler, F.data == "menu")
    dispatcher.callback_query.register(answer_before_search, F.data.in_({"all", "wiki", "git", "stack"}))
    dispatcher.message.register(answer_before_search, F.text)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())