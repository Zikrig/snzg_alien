from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import config
import vk_data_file
import st
import json


GROUP_ID = config.VK_GROUP_ID
GROUP_TOKEN = config.VK_GROUP_TOKEN
API_VERSION = config.VK_API_VERSION
HI = ['start', 'Start', 'начать', 'Начало', 'Начать', 'начало', 'Бот', 'бот', 'Старт', 'старт', 'скидки', 'Скидки']
MENU = ["Меню!", "Меню", "Запустить бота!"]
CALLBACK_TYPES = ('show_snackbar', 'open_link', 'open_app', 'text')
TEXT_INST = """
1. Для начала работы нажмите : "запустить бота"
2. Выберите нужную Вам  категорию, если не нашли на первой странице, нажмите : "далее"
Затем введите номер нужной услуги и отправьте сообщением боту. 
3. Также вы всегда можете найти актуальный перечень всех акций и предложений нажав кнопку : "таблица со всеми промокодами"
4. Чтобы всегда оставаться на связи, подпишитесь на нас в телеграмм канале, нажав кнопку : "Мы в Телеграме"
"""

vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

settings_reply = dict(one_time=False, inline=False)
settings_inline = dict(one_time=False, inline=True)

main_keyboard = VkKeyboard(**settings_reply)



main_keyboard.add_callback_button(label='Таблица со всеми промокодами!', color=VkKeyboardColor.POSITIVE, payload={"type": "open_link", "link": config.GOOGLE_SHEETS_URL})
main_keyboard.add_line()

main_keyboard.add_button(label='Запустить бота!', color=VkKeyboardColor.NEGATIVE, payload={"type": "text"})
main_keyboard.add_line()

main_keyboard.add_callback_button(label='Мы в Телеграме!', color=VkKeyboardColor.PRIMARY, payload={"type": "open_link", "link": config.TELEGRAM_CHANNEL_PUBLIC_URL})


main_keyboard_secondary = VkKeyboard(**settings_reply)
main_keyboard_secondary.add_callback_button(label='Таблица со всеми промокодами!', color=VkKeyboardColor.POSITIVE,
                                            payload={"type": "open_link",
                                                     "link": config.GOOGLE_SHEETS_URL})
main_keyboard_secondary.add_line()
main_keyboard_secondary.add_button(label='Меню!', color=VkKeyboardColor.NEGATIVE, payload={"type": "text"})
main_keyboard_secondary.add_line()
main_keyboard_secondary.add_callback_button(label='Мы в Телеграме!', color=VkKeyboardColor.PRIMARY,
                                            payload={"type": "open_link", "link": config.TELEGRAM_CHANNEL_PUBLIC_URL})


def keyboard_universal_slider(mass, flag, change_flag, slide_num=0, num_of_el=5):
    keyb = VkKeyboard(**settings_inline)
    try:
        mass.remove("")
    except:
        pass
    if len(mass) < (slide_num + 1) * num_of_el:
        lenght = len(mass)
    else:
        lenght = (slide_num + 1) * num_of_el

    for i in range(slide_num * num_of_el, lenght):
        d = {"type": flag, "data": str(i)}
        keyb.add_button(label=mass[i], color=VkKeyboardColor.SECONDARY, payload=d)

        keyb.add_line()

    if slide_num == 0 and len(mass)>=num_of_el:
        # первый
        keyb.add_callback_button(label="вперед", color=VkKeyboardColor.PRIMARY,
                                 payload={"type": change_flag, "data": str(slide_num + 1)})
    elif len(mass) > (slide_num + 1) * num_of_el:
        # посередине
        keyb.add_callback_button(label="назад", color=VkKeyboardColor.PRIMARY,
                                 payload={"type": change_flag, "data": str(slide_num - 1)})
        keyb.add_callback_button(label="вперед", color=VkKeyboardColor.PRIMARY,
                                 payload={"type": change_flag, "data": str(slide_num + 1)})

    else:
        keyb.add_callback_button(label="назад", color=VkKeyboardColor.PRIMARY,
                                 payload={"type": change_flag, "data": str(slide_num - 1)})
        # конец
    return keyb.get_keyboard()


def keyboard_universal_slider2(mass, flag, change_flag, slide_num=0, num_of_el=5, cat=""):
    keyb = VkKeyboard(**settings_inline)
    try:
        mass.remove("")
    except:
        pass
    if len(mass) < (slide_num + 1) * num_of_el:
        lenght = len(mass)
    else:
        lenght = (slide_num + 1) * num_of_el

    for i in range(slide_num * num_of_el, lenght):
        d = {"type": flag, "data": str(i), "name": mass[i]}
        keyb.add_callback_button(label=mass[i], color=VkKeyboardColor.SECONDARY, payload=d)

        keyb.add_line()

    if slide_num == 0 and len(mass)>num_of_el:
        # первый
        keyb.add_callback_button(label="вперед", color=VkKeyboardColor.PRIMARY,
                                 payload={"type": change_flag, "data": str(slide_num + 1), "cat": cat})
    elif len(mass) > (slide_num + 1) * num_of_el :
        # посередине
        keyb.add_callback_button(label="назад", color=VkKeyboardColor.PRIMARY,
                                 payload={"type": change_flag, "data": str(slide_num - 1), "cat": cat})
        keyb.add_callback_button(label="вперед", color=VkKeyboardColor.PRIMARY,
                                 payload={"type": change_flag, "data": str(slide_num + 1), "cat": cat})

    elif len(mass)<=num_of_el:
        keyb.add_button(label='Меню!', color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
    else:
        keyb.add_callback_button(label="назад", color=VkKeyboardColor.PRIMARY,
                                 payload={"type": change_flag, "data": str(slide_num - 1), "cat": cat})
        # конец
    return keyb.get_keyboard()


print("Ready")
def main_f():
    try: 
        for event in longpoll.listen():
            
                print(event)
            
                if event.type == VkBotEventType.MESSAGE_NEW:
                    # сообщения
                    if event.obj.message['text'] != '':
                        if event.from_user:
                            if event.obj.message['text'] in HI:
                                vk.messages.send(
                                    user_id=event.obj.message['from_id'],
                                    random_id=get_random_id(),
                                    peer_id=event.obj.message['from_id'],
                                    keyboard=main_keyboard.get_keyboard(),
                                    message=TEXT_INST)

                            if event.obj.message['text'] in MENU :
                                print(event.obj.message['text'])
                                vk.messages.send(
                                    user_id=event.obj.message['from_id'],
                                    random_id=get_random_id(),
                                    peer_id=event.obj.message['from_id'],
                                    keyboard=keyboard_universal_slider(mass=list(vk_data_file.main_dict.keys()), flag="1",
                                                                       change_flag="!"),
                                    message='Выбирайте категорию')

                            elif len(event.obj.message['text'])>4:
                                for x in list(vk_data_file.main_dict.keys()):
                                    if event.obj.message['text'].lower() in x.lower():
                                        st.join_new_stat_data("vk", str(event.obj.message['from_id']), str(x))
                                        vk.messages.send(
                                            user_id=event.obj.message['from_id'],
                                            random_id=get_random_id(),
                                            peer_id=event.obj.message['from_id'],
                                            keyboard=keyboard_universal_slider2(mass=list(vk_data_file.main_dict[x]), flag="2",
                                                                                change_flag="@", cat=x),
                                            message='Выбирайте магазин')

                        if event.obj.message['text'] == config.admin_command("refresh_GS"):
                            vk_data_file.regenerate()
                            vk.messages.send(
                                user_id=event.obj.message['from_id'],
                                random_id=get_random_id(),
                                peer_id=event.obj.message['from_id'],
                                message='обновление таблицы прошло успешно')

                elif event.type == VkBotEventType.MESSAGE_EVENT:
                    # callback
                    if event.object.payload.get('type') in CALLBACK_TYPES:
                    
                            vk.messages.sendMessageEventAnswer(
                                  event_id=event.object.event_id,
                                  user_id=event.object.user_id,
                                  peer_id=event.object.peer_id,                                                   
                                  event_data=json.dumps(event.object.payload))
                    
                    if event.object.payload.get('type') == "!":
                        vk.messages.edit(
                            peer_id=event.obj.peer_id,
                            conversation_message_id=event.obj.conversation_message_id,
                            keyboard=keyboard_universal_slider(mass=list(vk_data_file.main_dict.keys()), flag="1", change_flag="!",
                                                               slide_num=int(event.object.payload.get('data'))),
                            message='Выбирай категорию')
                        
                    elif event.object.payload.get('type') == "@":
                        vk.messages.edit(
                            peer_id=event.obj.peer_id,
                            conversation_message_id=event.obj.conversation_message_id,
                            keyboard=keyboard_universal_slider2(
                                mass=list(vk_data_file.main_dict[event.object.payload.get('cat')]), flag="2",
                                change_flag="@", slide_num=int(event.object.payload.get('data')),
                                cat=event.object.payload.get('cat')),
                            message='Выбирай категорию')
                    elif event.object.payload.get('type') == "2":

                        st.join_new_stat_data("vk", str(event.obj['user_id']), str(event.object.payload.get('name')))
                        for x in vk_data_file.text_dict[event.object.payload.get('name')]:
                            vk.messages.send(
                                user_id=event.obj['user_id'],
                                random_id=get_random_id(),
                                peer_id=event.obj['peer_id'],
                                message=x)
                        vk.messages.send(
                            user_id=event.obj['user_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj['peer_id'],
                            message="нажмите Меню, для вызова главного меню",
                            keyboard=main_keyboard_secondary.get_keyboard())
   
    except:
        main_f()
main_f()

