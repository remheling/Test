import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, OWNER_ID
from database import init_db
import handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    # Инициализация базы данных
    init_db()
    
    # Регистрация обработчиков
    handlers.register_handlers(dp, bot)
    
    # Уведомление о запуске
    await bot.send_message(OWNER_ID, "✅ Бот запущен и готов к работе!")
    logger.info("Бот успешно запущен")
    
    # Запуск поллинга
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())