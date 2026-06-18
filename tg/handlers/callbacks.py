import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
import data_file
import st
from tg.channel import user_left_channel
from tg.keyboards import (
    all_markets_keyb,
    back_keyboard_gen,
    main_keyboard_gen,
    secondary_keyboard_gen,
    semi_secondary_keyboard_gen,
)
from tg.states import PromoVerifyStates

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data)
async def query_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not callback.data or not callback.message:
        return

    data = callback.data[1:]
    flag = callback.data[0]

    if flag == "*":
        await callback.message.edit_text(
            "Выбирайте 🥰",
            reply_markup=all_markets_keyb,
        )

    if flag == "1":
        st.join_new_stat_data("tg", callback.from_user.id, data)
        await callback.message.edit_text(
            "Выбирайте 🥰",
            reply_markup=secondary_keyboard_gen(data),
        )

    if flag == "2":
        await callback.message.edit_text(
            "Выбирайте 🥰",
            reply_markup=semi_secondary_keyboard_gen(data),
        )

    if flag == "3":
        if "u" not in data:
            row = data_file.main_list[int(data)]
            logger.info(
                "promo_regular: user=%s callback=%r promo_id=%s name=%r discount=%r code=%r",
                callback.from_user.id,
                callback.data,
                data,
                row[0],
                row[3],
                row[2],
            )
            await callback.message.answer(
                "Чтобы воспользоваться акцией необходимо: перейти по ссылке или "
                "скопировать промокод и ввести его на сайте или приложении магазина"
            )
            await callback.message.answer(data_file.text_dict[data])
            st.join_new_stat_data("tg", callback.from_user.id, data_file.main_list[int(data)][0])

            keyb_local = back_keyboard_gen(data)
            if await user_left_channel(callback.bot, callback.from_user.id):
                rows = list(keyb_local.inline_keyboard) + [
                    [
                        InlineKeyboardButton(
                            text="Подпишитесь на канал!",
                            url=config.TELEGRAM_CHANNEL_INVITE_URL,
                        )
                    ]
                ]
                keyb_local = InlineKeyboardMarkup(inline_keyboard=rows)

            await callback.message.answer(
                "Куда отправимся за скидками дальше?",
                reply_markup=keyb_local,
            )
        else:
            meta = data_file.get_unicum_meta(data)
            codes_left = len(data_file.unicum_sheet.get(data, []))
            if data_file.user_has_got_promo(callback.message.chat.id, data):
                logger.info(
                    "promo_request: user=%s promo=%s shop=%r label=%r — already_used",
                    callback.message.chat.id,
                    data,
                    meta.get("shop"),
                    meta.get("label"),
                )
                await callback.message.answer("Вы уже использовали промокод")
            elif not data_file.unicum_sheet.get(data):
                logger.warning(
                    "promo_request: user=%s promo=%s shop=%r label=%r — no_codes_left",
                    callback.message.chat.id,
                    data,
                    meta.get("shop"),
                    meta.get("label"),
                )
                await callback.message.answer("Промокоды закончились")
            else:
                logger.info(
                    "promo_request: user=%s callback=%r promo=%s shop=%r label=%r category=%r "
                    "codes_available=%d — sending instructions",
                    callback.message.chat.id,
                    callback.data,
                    data,
                    meta.get("shop"),
                    meta.get("label"),
                    meta.get("category"),
                    codes_left,
                )
                await callback.message.answer(
                    data_file.text_dict[data] + "\n" + data_file.link_try_dict[data][1],
                )
                await state.set_state(PromoVerifyStates.waiting_phrase)
                await state.update_data(
                    promo_key=data,
                    phrase=data_file.link_try_dict[data][2],
                )

    if flag == "b":
        if data == "m":
            await callback.message.edit_text(
                "Выберите категорию в которой хотите получить скидку ⬇",
                reply_markup=main_keyboard_gen(),
            )
