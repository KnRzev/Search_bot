import asyncio, html, aiohttp
from aiogram.fsm.context import FSMContext
from ui import back_to_menu

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