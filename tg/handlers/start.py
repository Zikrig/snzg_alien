import asyncio

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile, Message

import config
import data_file
import st
from tg.keyboards import (
    all_markets_keyb,
    main_keyb_cat_market,
    main_keyboard_gen,
    rebuild_static_keyboards,
    semi_secondary_keyboard_gen,
)
from tg.states import PromoVerifyStates

router = Router()


@router.message(F.text, ~StateFilter(PromoVerifyStates.waiting_phrase))
async def handle_text(message: Message):
    text = message.text

    if text == "/start":
        await message.answer(
            "Рады вас видеть в SkidkiNezagorami",
            reply_markup=main_keyb_cat_market,
        )
        await message.answer(
            "Выберите категорию в которой хотите получить скидку ⬇",
            reply_markup=main_keyboard_gen(),
        )
        return

    if text == config.admin_command("refresh_GS"):
        await asyncio.to_thread(data_file.regenerate)
        rebuild_static_keyboards()
        await message.answer("обновление таблицы прошло упешно")
        return

    if text == config.admin_command("stat_output"):
        fn = await asyncio.to_thread(st.output_stat_frame)
        await message.answer_document(FSInputFile(fn))
        return

    if text == config.admin_command("stat_refresh"):
        st.refresh_stat()
        await message.answer("очистка статистика прошла упешно")
        return

    if text == "Категории":
        await message.answer(
            "Выберите категорию в которой хотите получить скидку ⬇",
            reply_markup=main_keyboard_gen(),
        )
        return

    if text == "Магазины":
        await message.answer("Выбирайте 🥰", reply_markup=all_markets_keyb)
        return

    if text in data_file.semi_dict:
        await message.answer(
            "Выбирайте 🥰",
            reply_markup=semi_secondary_keyboard_gen(text),
        )
