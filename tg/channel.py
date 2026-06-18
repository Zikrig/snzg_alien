import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

import config

logger = logging.getLogger(__name__)


async def user_left_channel(bot: Bot, user_id: int) -> bool:
    """Return True if user is not subscribed. False if subscribed or check unavailable."""
    try:
        member = await bot.get_chat_member(config.TELEGRAM_CHANNEL_USERNAME, user_id)
        return member.status in ("left", "kicked")
    except TelegramBadRequest as exc:
        logger.warning(
            "Channel subscription check failed for user=%s channel=%s: %s",
            user_id,
            config.TELEGRAM_CHANNEL_USERNAME,
            exc,
        )
        return False
