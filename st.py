import json
import data_file
import vk_data_file
import time
import time


vk_stat_dict = {}
tg_stat_dict = {}

def refresh_stat():
    global vk_stat_dict,tg_stat_dict
    vk_stat_dict = {}
    tg_stat_dict = {}


def join_new_stat_data(place,user_id,data):
    global vk_stat_dict,tg_stat_dict
    if place == "tg":
        try:
            tg_stat_dict[data].append(user_id)
        except:
            tg_stat_dict[data] = [user_id]
    elif place == "vk":
        try:
            vk_stat_dict[data].append(user_id)
        except:
            vk_stat_dict[data] = [user_id]



def output_stat_frame():


    global vk_stat_dict,tg_stat_dict
    text = "В статистике указанны только уникальные просмотры\n\n\n"
    t1 = "Категории тг\n"
    t2 = "Магазины тг\n"
    t3 = "Категории вк\n"
    t4 = "Магазины вк\n"
    for k,v in tg_stat_dict.items():
        if k in list(data_file.main_dict.keys()):
            t1 += f"{k}: {len(set(v))}"
        else:
            t2 += f"{k}: {len(set(v))}"

    for k,v in vk_stat_dict.items():
        if k in list(vk_data_file.main_dict.keys()):
            t3 += f"{k}: {len(set(v))}"
        else:
            t4 += f"{k}: {len(set(v))}"

    text = f"{text}{t1}\n{t2}\n{t3}\n{t4}"
    fn = f"{str(int(time.time()))}.txt"
    with open(fn, "w", encoding="utf-8") as f:
        f.write(text)
    return fn
