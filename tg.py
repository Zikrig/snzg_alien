import logging

import telebot

from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InputMediaPhoto
import config
import data_file
import st

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
user_import_dict = {}

main_keyb_cat_market = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyb_cat_market.add(KeyboardButton("Категории"),KeyboardButton("Магазины"))


def main_keyboard_gen():
    main_keyboard = InlineKeyboardMarkup()
    temp = data_file.main_dict.keys()
    main_keyboard.add(InlineKeyboardButton("Список магазинов",callback_data="*"))
    for x in temp:
        main_keyboard.add(InlineKeyboardButton(x, callback_data="1" + x))
    main_keyboard.add(InlineKeyboardButton("Таблица со всеми Промокодами!",url=config.GOOGLE_SHEETS_URL))
    return main_keyboard
    
def secondary_keyboard_gen(cat):
    secondary_keyboard = InlineKeyboardMarkup()
    temp = data_file.main_dict[cat]
    for x in temp:
        secondary_keyboard.add(InlineKeyboardButton(x,callback_data="2"+str(x)))
    secondary_keyboard.add(InlineKeyboardButton("В меню",callback_data = "bm"))
    return secondary_keyboard

def semi_secondary_keyboard_gen(market):
    semi_secondary_keyboard = InlineKeyboardMarkup()
    temp = data_file.semi_dict[market]
    for el,ind in temp:
        semi_secondary_keyboard.add(InlineKeyboardButton(el,callback_data="3"+str(ind)))
    semi_secondary_keyboard.add(InlineKeyboardButton("В меню",callback_data = "bm"))
    return semi_secondary_keyboard


def back_keyboard_gen(market):
    back_keyboard = InlineKeyboardMarkup()
    
    back_keyboard.add(InlineKeyboardButton("В меню",callback_data = "bm"))
    for k,v in data_file.main_dict.items():
        if market in v:
            back_keyboard.add(InlineKeyboardButton(k, callback_data="1"+k))
    return back_keyboard

all_markets_keyb = InlineKeyboardMarkup()
tem = list(sorted(data_file.semi_dict.keys()))
for i in range(0, len(tem), 3):
    tempr = tem[i : i + 3]
    l = []
    for j in tempr:
        l.append(InlineKeyboardButton(j,callback_data = "2"+j))
    all_markets_keyb.add(*l)
all_markets_keyb.add(InlineKeyboardButton("В меню",callback_data = "bm"))

to_menu_keyb = InlineKeyboardMarkup()
to_menu_keyb.row(InlineKeyboardButton("В меню",callback_data = "bm"))

@bot.message_handler(content_types=['text'])
def start(message):
    global user_import_dict

    if message.text == '/start':
        bot.send_message(message.chat.id,"Рады вас видеть в SkidkiNezagorami", reply_markup=main_keyb_cat_market)
        bot.send_message(message.chat.id, "Выберите категорию в которой хотите получить скидку ⬇",reply_markup=main_keyboard_gen())
    elif message.text == config.admin_command("refresh_GS"):
        data_file.regenerate()
        bot.send_message(message.chat.id, "обновление таблицы прошло упешно")
    elif message.text == config.admin_command("stat_output"):
        fn = st.output_stat_frame()
        with open(fn, "r", encoding="utf-8") as f:
            bot.send_document(message.chat.id,document=f)
    elif message.text == config.admin_command("stat_refresh"):
        st.refresh_stat()
        bot.send_message(message.chat.id, "очистка статистика прошла упешно")
    elif message.text == "Категории":
        bot.send_message(message.chat.id, "Выберите категорию в которой хотите получить скидку ⬇",reply_markup=main_keyboard_gen())
        
    elif message.text == "Магазины":
        bot.send_message(message.chat.id,"Выбирайте 🥰" ,reply_markup = all_markets_keyb)
    elif message.text in data_file.semi_dict:
        bot.send_message(message.chat.id,"Выбирайте 🥰",reply_markup=semi_secondary_keyboard_gen(message.text))
        
    else:
        pending = user_import_dict.get(message.chat.id)
        if not pending:
            return

        logger.info(
            "promo_verify: user=%s pending=%s text=%r",
            message.chat.id,
            pending[0],
            message.text[:80] if message.text else None,
        )

        if pending[2] not in message.text:
            logger.warning(
                "promo_verify: user=%s — phrase mismatch, expected substring=%r",
                message.chat.id,
                pending[2],
            )
            bot.send_message(message.chat.id, "что-то пошло не так, поробуйте снова")
            return

        promo_key = pending[0]
        try:
            promo_code = data_file.issue_unicum_promo(message.chat.id, promo_key)
        except ValueError as exc:
            if str(exc) == "already_used":
                bot.send_message(message.chat.id, "Вы уже использовали промокод")
            elif str(exc) == "no_codes_left":
                bot.send_message(message.chat.id, "Промокоды закончились")
            else:
                bot.send_message(message.chat.id, "что-то пошло не так, поробуйте снова")
            user_import_dict.pop(message.chat.id, None)
            return
        except Exception:
            logger.exception("Failed to issue promo for user %s", message.chat.id)
            bot.send_message(message.chat.id, "Не удалось выдать промокод, попробуйте позже")
            return

        user_import_dict.pop(message.chat.id, None)
        bot.send_message(message.chat.id, f"<code>{promo_code}</code>", parse_mode="HTML")
        bot.send_message(
            message.chat.id,
            "Куда отправимся за скидками дальше?",
            reply_markup=to_menu_keyb,
        )

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global user_import_dict
    bot.answer_callback_query(callback_query_id=call.id, )
    data = call.data[1:]
    flag = call.data[0]
    if flag == "*":
        bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id,text = "Выбирайте 🥰" ,reply_markup = all_markets_keyb)
    
    if flag == "1":
        st.join_new_stat_data("tg",call.from_user.id,data)
        bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id, text="Выбирайте 🥰",  reply_markup=secondary_keyboard_gen(data) )
    
    if flag == "2":
        bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id, text="Выбирайте 🥰", reply_markup=semi_secondary_keyboard_gen(data) )
        
    if flag == '3':
        

        
        #u in data
        if 'u' not in data:
            bot.send_message(call.message.chat.id,"Чтобы воспользоваться акцией необходимо: перейти по ссылке или скопировать промокод и ввести его на сайте или приложении магазина")
            bot.send_message(call.message.chat.id, data_file.text_dict[data],parse_mode="HTML")
            st.join_new_stat_data("tg", call.from_user.id, data_file.main_list[int(data)][0])
            
            user_channel_status = bot.get_chat_member(chat_id=config.TELEGRAM_CHANNEL_USERNAME, user_id=call.message.chat.id)
            
            keyb_local = back_keyboard_gen(data)

            if user_channel_status.status == "left":
                keyb_local.add(InlineKeyboardButton("Подпишитесь на канал!",url = config.TELEGRAM_CHANNEL_INVITE_URL))
            
            bot.send_message(call.message.chat.id, "Куда отправимся за скидками дальше?" ,
                             reply_markup=keyb_local)
        else:
            if data_file.user_has_got_promo(call.message.chat.id, data):
                bot.send_message(call.message.chat.id, "Вы уже использовали промокод")
            elif not data_file.unicum_sheet.get(data):
                bot.send_message(call.message.chat.id, "Промокоды закончились")
            else:
                logger.info("promo_start: user=%s promo=%s — sending instructions", call.message.chat.id, data)
                bot.send_message(
                    call.message.chat.id,
                    data_file.text_dict[data] + "\n" + data_file.link_try_dict[data][1],
                )
                user_import_dict[call.message.chat.id] = data_file.link_try_dict[data]
        
    if flag == "b":
        if data == "m":
            bot.edit_message_text(message_id=call.message.message_id,chat_id=call.message.chat.id,
                                  text="Выберите категорию в которой хотите получить скидку ⬇",
                                  reply_markup=main_keyboard_gen())




def start_polling():
    webhook = bot.get_webhook_info()
    if webhook.url:
        logger.warning("Active webhook %s — removing before polling", webhook.url)
    bot.delete_webhook()
    logger.info("Telegram bot started in polling mode")
    bot.infinity_polling()


start_polling()

