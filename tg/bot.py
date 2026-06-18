import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramConflictError
from aiogram.fsm.storage.memory import MemoryStorage

import config
from tg.handlers import setup_routers

logger = logging.getLogger(__name__)


async def run():
    bot = Bot(
        token=config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    setup_routers(dp)

    webhook = await bot.get_webhook_info()
    if webhook.url:
        logger.warning("Active webhook %s — removing before polling", webhook.url)
    await bot.delete_webhook(drop_pending_updates=False)
    logger.info("Telegram bot started in polling mode")

    try:
        await dp.start_polling(bot, handle_signals=False)
    except TelegramConflictError:
        logger.error(
            "Another process is polling the same Telegram bot token; stopping Telegram bot."
        )
    finally:
        await bot.session.close()


def start_polling():
    asyncio.run(run())
