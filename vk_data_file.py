
import gspread
import config

main_dict = {}
text_dict = {}

def regenerate():
    global main_dict, text_dict
    gc = gspread.service_account(filename=config.GOOGLE_SERVICE_ACCOUNT_FILE)
    sht2 = gc.open_by_url(config.GOOGLE_SHEETS_URL)
    worksheet = sht2.sheet1
    main_list = worksheet.get_all_values()
    main_dict = {}
    text_dict = {}
    header = main_list[0]

    for el in main_list[1:]:
        try:
            if el[0] not in main_dict[el[8]]:
                main_dict[el[8]].append(el[0])
        except:
            main_dict[el[8]] = [el[0]]

        text = ""        
        text += f"Название: {el[0]}\n"
    
        text += f"Скидка: {el[3]}\n"
                
        text += f"Ссылка: {el[4]}\n"

        text += f"Действует до: {el[5]}\n"

        text += f"Регион: {el[6]}\n"

        text += f"Условия акции: {el[7]}\n"

        text += f"Промокод ниже⬇️ "
        

        
        try:
            text_dict[el[0]].append(text)
            text_dict[el[0]].append(el[2])
        except:
            text_dict[el[0]] = [text]
            text_dict[el[0]].append(el[2])

regenerate()
print(main_dict.keys())

