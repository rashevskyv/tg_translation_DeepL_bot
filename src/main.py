import asyncio
import logging
import sys
from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.config import settings
from src.database.db import db_manager
from src.handlers.settings import settings_router
from src.handlers.translation import translation_router


async def main() -> None:
    # Setup logging
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger("tg_translator_bot")
    logger.info("Initializing Translation Bot...")

    if not settings.bot_token:
        logger.error(
            "BOT_TOKEN is not set in environment or .env file! Please configure BOT_TOKEN before running the bot."
        )
        sys.exit(1)

    # Initialize SQLite database
    await db_manager.init_db()
    logger.info(f"Database initialized at {settings.database_path}")

    # Setup Bot and Dispatcher
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers
    dp.include_router(settings_router)
    dp.include_router(translation_router)

    # Register Telegram native command menu
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="settings", description="⚙️ Open settings (Languages, Engines, API keys)"),
        BotCommand(command="start", description="🚀 Start bot & view current preferences"),
        BotCommand(command="help", description="📖 Help & Supported providers guide"),
    ])
    logger.info("Bot commands registered in Telegram menu.")

    logger.info("Bot routers registered. Starting long polling...")
    try:
        # Drop pending updates to avoid processing backlog
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        logger.info("Closing bot session...")
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
