from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from search import all_search, git_search, stack_search, wiki_search
from ui import back_to_menu, menu_keyboard

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
