import aiogram, asyncio, os, dotenv
dotenv.load_dotenv()
from aiogram import F
from aiogram.filters import Command
from logic import answer_before_search, menu_handler, start_handler

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