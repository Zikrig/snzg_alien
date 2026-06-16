import itertools
import logging
import string
import threading
import time
from pathlib import Path

import gspread

import config

logger = logging.getLogger(__name__)

LOG_DIR = Path(__file__).resolve().parent / "logs"

main_dict = {}
text_dict = {}
gc = gspread.service_account(filename=config.GOOGLE_SERVICE_ACCOUNT_FILE)
sht2 = gc.open_by_url(config.GOOGLE_SHEETS_URL)
worksheet = sht2.worksheet("Промокоды")
worksheet2 = sht2.worksheet("Разовые промы")

COLUMN_LETTERS = [
    "".join(x)
    for x in (
        list(itertools.product(string.ascii_uppercase, repeat=1))
        + list(itertools.product(string.ascii_uppercase, repeat=2))
    )
]

# {telegram_user_id: {column_index, ...}}
got_promos = {}
promo_lock = threading.Lock()

# {promo_key: {"category", "shop", "label"}}
unicum_meta = {}


def get_unicum_meta(promo_key):
    return unicum_meta.get(promo_key, {})


def log_unicum_inventory():
    """Log one-time promo articles and available code counts after sheet reload."""
    if not unicum_meta:
        logger.info("unicum_inventory: no one-time promos loaded")
        return

    lines = []
    for promo_key in sorted(unicum_meta, key=lambda k: int(k.replace("u", ""))):
        meta = unicum_meta[promo_key]
        codes_left = len(unicum_sheet.get(promo_key, []))
        lines.append(
            f"  {promo_key}: shop={meta['shop']!r} label={meta['label']!r} "
            f"category={meta['category']!r} codes_available={codes_left}"
        )
    logger.info(
        "unicum_inventory: %d article(s) with one-time promos:\n%s",
        len(lines),
        "\n".join(lines),
    )


def cell_done(cell, user_id):
    """Mark a promo cell as taken. One API call — format removed to stay within Sheets quota."""
    value = f"@*{user_id}"
    last_error = None
    for attempt in range(3):
        try:
            worksheet2.update([[value]], range_name=cell)
            logger.info("cell_done OK: cell=%s user_id=%s value=%s", cell, user_id, value)
            return
        except Exception as exc:
            last_error = exc
            logger.exception(
                "cell_done FAILED: cell=%s user_id=%s (attempt %d/%d)",
                cell,
                user_id,
                attempt + 1,
                3,
            )
            time.sleep(attempt + 1)
    raise last_error


_EMPTY_PROMOS = frozenset()


def user_has_got_promo(user_id, promo_key):
    col_ind = int(promo_key.replace("u", ""))
    return col_ind in got_promos.get(str(user_id), _EMPTY_PROMOS)


def issue_unicum_promo(user_id, promo_key):
    """Reserve a one-time promo code and mark it in the sheet."""
    col_ind = int(promo_key.replace("u", ""))
    user_id_str = str(user_id)
    meta = get_unicum_meta(promo_key)

    with promo_lock:
        if col_ind in got_promos.get(user_id_str, set()):
            logger.info(
                "issue_unicum_promo: user=%s promo=%s shop=%r label=%r — already_used",
                user_id,
                promo_key,
                meta.get("shop"),
                meta.get("label"),
            )
            raise ValueError("already_used")

        queue = unicum_sheet.get(promo_key, [])
        if not queue:
            logger.warning(
                "issue_unicum_promo: user=%s promo=%s shop=%r label=%r — no_codes_left",
                user_id,
                promo_key,
                meta.get("shop"),
                meta.get("label"),
            )
            raise ValueError("no_codes_left")

        promo_ind, promo_code = queue[0]
        unicum_sheet[promo_key] = queue[1:]
        cell = COLUMN_LETTERS[col_ind] + str(promo_ind + 7)
        logger.info(
            "issue_unicum_promo: user=%s promo=%s shop=%r label=%r category=%r "
            "cell=%s code=%s codes_left_after=%d — writing to sheet",
            user_id,
            promo_key,
            meta.get("shop"),
            meta.get("label"),
            meta.get("category"),
            cell,
            promo_code,
            len(unicum_sheet[promo_key]),
        )

        try:
            cell_done(cell, user_id)
        except Exception:
            unicum_sheet[promo_key] = queue
            logger.error(
                "issue_unicum_promo: user=%s promo=%s cell=%s — sheet write failed, rolled back",
                user_id,
                promo_key,
                cell,
            )
            raise

        got_promos.setdefault(user_id_str, set()).add(col_ind)
        logger.info(
            "issue_unicum_promo: user=%s promo=%s shop=%r label=%r — done",
            user_id,
            promo_key,
            meta.get("shop"),
            meta.get("label"),
        )
        return promo_code


def regenerate():
    global main_dict, text_dict, semi_dict, main_list, unicum_sheet, got_promos, link_try_dict, unicum_meta
    main_list = worksheet.get_all_values()
    main_list2 = worksheet2.get_all_values()
    main_dict = {}
    semi_dict = {}
    text_dict = {}
    unicum_sheet = {}
    link_try_dict = {}
    got_promos = {}
    unicum_meta = {}
    header = main_list[0]

    for ind, el in enumerate(main_list[1:], start=1):
        try:
            if el[0] not in main_dict[el[8]]:
                main_dict[el[8]].append(el[0])
        except Exception:
            main_dict[el[8]] = [el[0]]

        try:
            if (el[3], ind) not in semi_dict[el[0]]:
                semi_dict[el[0]].append((el[3], ind))
        except Exception:
            semi_dict[el[0]] = [(el[3], ind)]

        text = ""
        text += f"Название: {el[0]}\n"
        text += f"Скидка: {el[3]}\n"
        text += f"Ссылка: {el[4]}\n"
        text += f"Действует до: {el[5]}\n"
        text += f"Регион: {el[6]}\n"
        text += f"Условия акции: {el[7]}\n"
        text += f"Промокод : <code>{el[2]}</code> "

        text_dict[str(ind)] = text

    a = list(zip(*main_list2[::-1]))

    for ind, el in enumerate(a):
        el = el[::-1]

        try:
            if el[1] not in main_dict[el[0]]:
                main_dict[el[0]].append(el[1])
        except Exception:
            main_dict[el[0]] = [el[1]]

        try:
            if (el[2], str(ind) + "u") not in semi_dict[el[1]]:
                semi_dict[el[1]].append((el[2], str(ind) + "u"))
        except Exception:
            semi_dict[el[1]] = [(el[2], str(ind) + "u")]

        promo_key = str(ind) + "u"
        text_dict[promo_key] = el[3]
        unicum_sheet[promo_key] = []
        unicum_meta[promo_key] = {
            "category": el[0],
            "shop": el[1],
            "label": el[2],
        }
        link_try_dict[promo_key] = [promo_key, el[4], el[5]]
        for indx, promo in enumerate(el[6:]):
            if promo[:2] == "@*":
                got_promos.setdefault(promo[2:], set()).add(ind)
            elif promo == "":
                pass
            else:
                unicum_sheet[promo_key].append((indx, promo))

    log_unicum_inventory()


regenerate()
