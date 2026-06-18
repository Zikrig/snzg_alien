from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

import config
import data_file

main_keyb_cat_market = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Категории"), KeyboardButton(text="Магазины")],
    ],
    resize_keyboard=True,
)

to_menu_keyb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="В меню", callback_data="bm")]],
)

all_markets_keyb: InlineKeyboardMarkup | None = None


def rebuild_static_keyboards():
    global all_markets_keyb
    tem = list(sorted(data_file.semi_dict.keys()))
    rows = []
    for i in range(0, len(tem), 3):
        rows.append(
            [
                InlineKeyboardButton(text=j, callback_data="2" + j)
                for j in tem[i : i + 3]
            ]
        )
    rows.append([InlineKeyboardButton(text="В меню", callback_data="bm")])
    all_markets_keyb = InlineKeyboardMarkup(inline_keyboard=rows)


def main_keyboard_gen():
    rows = [[InlineKeyboardButton(text="Список магазинов", callback_data="*")]]
    for x in data_file.main_dict.keys():
        rows.append([InlineKeyboardButton(text=x, callback_data="1" + x)])
    rows.append(
        [
            InlineKeyboardButton(
                text="Таблица со всеми Промокодами!",
                url=config.GOOGLE_SHEETS_URL,
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def secondary_keyboard_gen(cat):
    rows = [
        [InlineKeyboardButton(text=x, callback_data="2" + str(x))]
        for x in data_file.main_dict[cat]
    ]
    rows.append([InlineKeyboardButton(text="В меню", callback_data="bm")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def semi_secondary_keyboard_gen(market):
    rows = [
        [InlineKeyboardButton(text=el, callback_data="3" + str(ind))]
        for el, ind in data_file.semi_dict[market]
    ]
    rows.append([InlineKeyboardButton(text="В меню", callback_data="bm")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_keyboard_gen(market):
    rows = [[InlineKeyboardButton(text="В меню", callback_data="bm")]]
    for k, v in data_file.main_dict.items():
        if market in v:
            rows.append([InlineKeyboardButton(text=k, callback_data="1" + k)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


rebuild_static_keyboards()
