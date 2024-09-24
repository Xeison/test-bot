import asyncio

from g4f.client import AsyncClient
from g4f.Provider import Ecosia

from aiogram import (Router, Bot, Dispatcher,
                     F, types)
import logging

# Название роутера
name = "business_router"

# Создание роутера
router = Router(name=name)
lock = asyncio.Lock()  # Блокировка для предотвращения одновременного доступа к асинхронному клиенту

# Настройка логгирования
logger = logging.getLogger(name)
logging.basicConfig(level=logging.INFO)


async def response_(message):
    """Обработка запроса к API."""
    client = AsyncClient(
        provider=Ecosia
    )
    # Провайдер Ecosia не работает в РФ, если вы не из РФ или сервер не РФ, можете неиспользовать ** и удалить строку ниже
    client.proxies = {
        "http": "https://user:pass@ip:port",
        "https": "https://user:pass@ip:port"
    }

    try:
        completion = await client.chat.completions.create(
            max_tokens=4096,
            model="gpt-3.5-turbo",  # Замените на имя модели
            messages=message,
        )

        return completion.choices[0].message.content

    except Exception as ex:
        print(ex)
        return None


@router.message(F.text)
async def handler_message(message: types.Message):
    """Обработка текстовых сообщений."""
    async with lock:
        user_id = message.chat.id
        logger.info(f"Received message from {user_id}: {message.text}")

        messages = [
            {"role": "system",
             "content": "Привет! Ты - ИИ-помощник для бизнеса в Telegram. Отвечай на вопросы пользователей"},
            {"role": "user", "content": message.text}
        ]

        response = await response_(messages)

        if response is None:
            await message.answer("Я не понимаю вас. Попробуй еще раз.")
        else:
            logger.info(f"Response sent to business chat: {response}")
            await message.answer(response)

    from dotenv import load_dotenv  # В самый верх файла

    async def main() -> None:
        """Запуск бота."""

    load_dotenv()
    API_TOKEN = os.getenv('API_TOKEN')
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())