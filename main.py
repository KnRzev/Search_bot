import os, dotenv
dotenv.load_dotenv()
import asyncio, aiogram, aiohttp, html
from aiogram import F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.fsm.context import FSMContext

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



async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Приветствую!\n"
        "Этот бот поможет вам найти статьи, на интересующие вас темы, на таких сайтах как:\n"
        "Wikipedia, Github и Stackoverflow\n"
        "Ниже выберете нужный сайт для поиска.", reply_markup=menu_keyboard)


async def menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.delete()
        await callback.message.answer("Выберите сайт, на котором хотите найти интересующую вас тему:", reply_markup=menu_keyboard)


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
            "Wikipedia, Github и Stackoverflow" : all_search,
            "Wikipedia" : wiki_search,
            "Github" : git_search,
            "Stackoverflow" : stack_search,
        }

        func = search_func[source]
        query = event.text
        website = source
        await state.update_data(source="in_search")
        reply = await func(event, query, state, flag = 1)

        if not reply:
            return

        await event.answer(f"На сайте {website} по вашему запросу на тему '{query}' найдено:\n\n"
                            + "\n\n".join(reply))

        await event.answer("Напишите следующую тему для поиска "
                           "или измените сайт для поиска через главное меню.", reply_markup=back_to_menu)

        if event.from_user is not None:
            username = event.from_user.username
            if not username:
                print("ID пользователя:", event.from_user.id)
            else:
                print("Пользователь:", f"@{username}")

        print("Выбранный сайт:", source)
        print("Введённый текст:", event.text)





async def all_search(event, query: str, state: FSMContext, flag):
    await event.delete()
    await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)
    flag -=1
    row_replies = await asyncio.gather(
        wiki_search(event, query, state, flag),
        git_search(event, query, state, flag),
        stack_search(event, query, state, flag)
    )
    reply = [text for row_reply in row_replies for text in row_reply]
    await state.update_data(source="Wikipedia, Github и Stackoverflow")
    return reply

async def wiki_search(event, query: str, state: FSMContext, flag):
    if flag:
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

    reply = []

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        async with session.get("https://ru.wikipedia.org/w/api.php", params=params) as response:
            response.raise_for_status()
            data = await response.json()

    if "error" in data:
        print("Ошибка API Wikipedia:", data["error"])
        await state.clear()
        if flag:
            await event.answer(
                "Не удалось выполнить поиск на Wikipedia. "
                "Попробуйте позже или вернитесь в главное меню.",
                reply_markup=back_to_menu,
            )
            return []
        else:
            reply.append("Не удалось выполнить поиск на Wikipedia.")
            return reply

    articles = data["query"]["search"]

    if not articles:
        if flag:
            await event.answer("По вашей теме ничего не найдено. Попробуйте задать другую тему "
                                "или вы можете вернуться в главное меню.", reply_markup=back_to_menu)
            await state.update_data(source="Wikipedia")
            return []
        else:
            reply.append("На Wikipedia по вашей теме ничего не найдено.")
            return reply

    for number, article in enumerate(articles, start=1):
        url = f"https://ru.wikipedia.org/?curid={article['pageid']}"
        reply.append(f"{number}. Название статьи: {article["title"]}\n"
                           f"Ссылка на статью: {url}")

    if flag:
        await state.update_data(source="Wikipedia")
    return reply


async def git_search(event, query: str, state: FSMContext, flag):
    if flag:
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

    reply = []

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        async with session.get("https://api.github.com/search/repositories", params=params) as response:
            status = response.status
            data = await response.json()

    if status >= 400:
        print("Ошибка API GitHub:", data)
        await state.clear()
        if flag:
            await event.answer(
                "Не удалось выполнить поиск на GitHub. "
                "Попробуйте позже или вернитесь в главное меню.",
                reply_markup=back_to_menu)
            return []
        else:
            reply.append("Не удалось выполнить поиск на GitHub.")
            return reply

    repositories = data["items"]

    if not repositories:
        if flag:
            await event.answer(
                "По вашей теме ничего не найдено. Попробуйте задать другую тему "
                "или вы можете вернуться в главное меню.", reply_markup=back_to_menu)
            await state.update_data(source="Github")
            return []
        else:
            reply.append("На Github по вашей теме ничего не найдено.")
            return reply

    for number, repository in enumerate(repositories, start=1):
        url = repository["html_url"]
        reply.append(f"{number}. Название проекта: {repository['full_name']}\nСсылка на проект: {url}")

    if flag:
        await state.update_data(source="Github")
    return reply


async def stack_search(event, query: str, state: FSMContext, flag):
    if flag:
        await event.delete()
        await event.bot.delete_message(chat_id=event.chat.id, message_id=event.message_id - 1)

    params = {
        "q": query,
        "site": "ru.stackoverflow.com",
        "pagesize": 3,
        "sort": "relevance",
        "order": "desc",
    }

    headers = {
        "User-Agent": "StudySearchBot (https://github.com/KnRzev/Search_bot)",
    }

    reply = []

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        async with session.get("https://api.stackexchange.com/2.3/search/advanced", params=params) as response:
            status = response.status
            data = await response.json()

    if status >= 400 or "error_id" in data:
        print("Ошибка API Stack Overflow:", data)
        await state.clear()
        if flag:
            await event.answer("Не удалось выполнить поиск на Stack Overflow. "
                "Попробуйте позже или вернитесь в главное меню.",
                reply_markup=back_to_menu)
            return []
        else:
            reply.append("Не удалось выполнить поиск на Stack Overflow.")
            return reply

    questions = data["items"]

    if not questions:
        if flag:
            await event.answer(
                "По вашей теме ничего не найдено. Попробуйте задать другую тему "
                "или вы можете вернуться в главное меню.", reply_markup=back_to_menu)
            await state.update_data(source="Stackoverflow")
            return []
        else:
            reply.append("На Stack Overflow по вашей теме ничего не найдено.")
            return reply

    for number, question in enumerate(questions, start=1):

        title = html.unescape(question["title"])
        url = f"https://ru.stackoverflow.com/q/{question['question_id']}"

        reply.append(f"{number}. Вопрос: {title}\nСсылка на вопрос: {url}")
    if flag:
        await state.update_data(source="Stackoverflow")
    return reply



async def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("Не удалось найти BOT_TOKEN")
    bot = aiogram.Bot(token=bot_token)
    dispatcher = aiogram.Dispatcher()

    dispatcher.message.register(start_handler, Command("start"))
    dispatcher.callback_query.register(menu_handler, F.data == "menu")
    dispatcher.callback_query.register(answer_before_search, F.data.in_({"Wikipedia, Github и Stackoverflow", "Wikipedia", "Github", "Stackoverflow"}))
    dispatcher.message.register(answer_before_search, F.text)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())