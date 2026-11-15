import os, dotenv

dotenv.load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не удалось найти BOT_TOKEN")


import asyncio, aiogram, aiohttp
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
            await event.answer("Сначала выберите сайт для поиска", reply_markup=menu_keyboard)
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

        if event.from_user is not None:
            username = event.from_user.username
            if not username:
                print("ID пользователя:", event.from_user.id)
            else:
                print("Пользователь:", f"@{username}")

        print("Выбранный сайт:", source)
        print("Введённый текст:", event.text)





async def all_search(event, query: str, state: FSMContext):
    await event.delete()
    await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)

    await event.answer(f"Ищу на всех сайтах по теме: {query}")

async def wiki_search(event, query: str, state: FSMContext):
    await event.delete()
    await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 3,
        "format": "json",
    }

    headers = {
        "User-Agent": "StudySearchBot (https://github.com/KnRzev/Search_bot) ",
    }

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        async with session.get("https://ru.wikipedia.org/w/api.php", params=params) as response:
            response.raise_for_status()
            data = await response.json()

    if "error" in data:
        print("Ошибка API Wikipedia:", data["error"])

        await event.answer(
            "Не удалось выполнить поиск на Wikipedia. "
            "Попробуйте позже или вернитесь в главное меню.",
            reply_markup=back_to_menu,
        )
        await state.clear()
        return

    articles = data["query"]["search"]

    if not articles:
        print("Ничего не найдено.")
        await event.answer("По вашей теме ничего не найдено. Попробуйте задать другую тему "
                           "или вы можете вернуться в главное меню.", reply_markup=back_to_menu)
        await state.update_data(source="wiki")

        return

    for number, article in enumerate(articles, start=1):

        if number == 1:
            await event.answer(f"По вашем запросу на тему '{query}' найдено:\n")

        url = f"https://ru.wikipedia.org/?curid={article['pageid']}"

        await event.answer(f"{number}. Название статьи: {article["title"]}\n"
                           f"Ссылка на статью: {url}")

    await event.answer("Напишите следующую тему для поиска "
                        "или измените сайт для поиска через главное меню.", reply_markup=back_to_menu)

    return


async def git_search(event, query: str, state: FSMContext):
    await event.delete()
    await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)

    params = {
        "q": query,
        "per_page": 3,
    }

    headers = {
        "User-Agent": "StudySearchBot (https://github.com/KnRzev/Search_bot)",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        async with session.get("https://api.github.com/search/repositories", params=params) as response:
            status = response.status
            data = await response.json()

    if status >= 400:
        print("Ошибка API GitHub:", data)

        await event.answer(
            "Не удалось выполнить поиск на GitHub. "
            "Попробуйте позже или вернитесь в главное меню.",
            reply_markup=back_to_menu,
        )
        await state.clear()
        return

    repositories = data["items"]

    if not repositories:
        print("Ничего не найдено.")

        await event.answer(
            "По вашей теме ничего не найдено. Попробуйте задать другую тему "
            "или вы можете вернуться в главное меню.", reply_markup=back_to_menu)
        await state.update_data(source="git")
        return

    for number, repository in enumerate(repositories, start=1):
        if number == 1:
            await event.answer(f"По вашему запросу на тему '{query}' найдено:\n")

        url = repository["html_url"]

        await event.answer(
            f"{number}. Название проекта: {repository['full_name']}\n"
            f"Ссылка на проект: {url}"
        )

    await event.answer(
        "Напишите следующую тему для поиска "
        "или измените сайт для поиска через главное меню.",
        reply_markup=back_to_menu,
    )

    return


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