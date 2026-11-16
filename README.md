# Поисковый асинхронный бот
Поисковые сайты бота: Wikipedia, GitHub, Stackoverflow

## Установка и запуск (Linux)

Для работы телеграмм бота нужно установить в виртуальное окружение три сторонние библиотеки:

aiogram - работа с Telegram

aiohttp - асинхронные запросы к API сайтов

python-dotenv - загрузка токена из .env

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install aiogram aiohttp python-dotenv
```
Файл .env имеет вид:
```bash
BOT_TOKEN=ваш_токен_от_BotFather
```
После установки зависимостей и настройки токена запустите бота.

```bash
python main.py
```

Бот запущен!