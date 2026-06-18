import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import data_file
from tg.keyboards import to_menu_keyb
from tg.states import PromoVerifyStates

logger = logging.getLogger(__name__)
router = Router()


@router.message(PromoVerifyStates.waiting_phrase, F.text)
async def verify_phrase(message: Message, state: FSMContext):
    data = await state.get_data()
    promo_key = data["promo_key"]
    phrase = data["phrase"]
    meta = data_file.get_unicum_meta(promo_key)

    logger.info(
        "promo_verify: user=%s promo=%s shop=%r label=%r text=%r",
        message.chat.id,
        promo_key,
        meta.get("shop"),
        meta.get("label"),
        message.text[:80] if message.text else None,
    )

    if phrase not in message.text:
        logger.warning(
            "promo_verify: user=%s promo=%s — phrase mismatch, expected substring=%r",
            message.chat.id,
            promo_key,
            phrase,
        )
        await message.answer("что-то пошло не так, поробуйте снова")
        return

    try:
        promo_code = await asyncio.to_thread(
            data_file.issue_unicum_promo,
            message.chat.id,
            promo_key,
        )
    except ValueError as exc:
        if str(exc) == "already_used":
            await message.answer("Вы уже использовали промокод")
        elif str(exc) == "no_codes_left":
            await message.answer("Промокоды закончились")
        else:
            await message.answer("что-то пошло не так, поробуйте снова")
        await state.clear()
        return
    except Exception:
        logger.exception("Failed to issue promo for user %s", message.chat.id)
        await message.answer("Не удалось выдать промокод, попробуйте позже")
        return

    await state.clear()
    await message.answer(f"<code>{promo_code}</code>")
    await message.answer(
        "Куда отправимся за скидками дальше?",
        reply_markup=to_menu_keyb,
    )
