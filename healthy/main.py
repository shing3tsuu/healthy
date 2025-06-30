from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from services.telegram.handlers import *
from services.telegram.telegram import *
from config_reader import load_config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    config = load_config(".env")
    tg_app = TelegramApp(config)
    await tg_app.setup()  # Теперь setup асинхронный
    await tg_app.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    winloop.install()
    asyncio.run(main())
