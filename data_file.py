import gspread
import config

main_dict = {}
text_dict = {}
gc = gspread.service_account(filename=config.GOOGLE_SERVICE_ACCOUNT_FILE)
sht2 = gc.open_by_url(config.GOOGLE_SHEETS_URL)
worksheet = sht2.worksheet("Промокоды")
worksheet2 = sht2.worksheet("Разовые промы")

got_promos = {}

def cell_done(cell,user_id):
    
    worksheet2.format(f"{cell}:{cell}", {
    "backgroundColor": {
      "red": 1.0,
      "green": 0.0,
      "blue": 0.0
    }})
    worksheet2.update(cell, f'@*{user_id}')

def regenerate():
    global main_dict, text_dict, semi_dict, main_list, unicum_sheet, got_promos, link_try_dict
    main_list = worksheet.get_all_values()
    main_list2 = worksheet2.get_all_values()
    main_dict = {}
    semi_dict = {}
    text_dict = {}
    unicum_sheet = {}
    link_try_dict = {}
    header = main_list[0]

    for ind,el in enumerate(main_list[1:],start=1):
        
        try:
            if el[0] not in main_dict[el[8]]:
                main_dict[el[8]].append(el[0])
        except:
            main_dict[el[8]] = [el[0]]

        try:
            if (el[3],ind) not in semi_dict[el[0]]:
                semi_dict[el[0]].append((el[3],ind))
        except:
            semi_dict[el[0]] = [(el[3],ind)]
        
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
    
    for ind,el in enumerate(a):
        el = el[::-1]
        #ind - индекс промокода
        
        try:
            if el[1] not in main_dict[el[0]]:
                main_dict[el[0]].append(el[1])
        except:
            main_dict[el[0]] = [el[1]]
        
        try:
            if (el[2],str(ind)+'u') not in semi_dict[el[1]]:
                semi_dict[el[1]].append((el[2],str(ind)+'u'))
        except:
            semi_dict[el[1]] = [(el[2],str(ind)+'u')]

        
        text_dict[str(ind)+'u']= el[3]
        unicum_sheet[str(ind)+'u'] = []
        link_try_dict[str(ind)+'u'] = [str(ind)+'u',el[4],el[5]]
        for indx,promo in list(enumerate(el[6:len(el)])):
            
            #indx - индекс уникальной итерации промокода
            if promo[:2] == "@*":
                try:
                    if ind not in got_promos[promo[2:]]:
                        got_promos[promo[2:]].append(ind)
                except:
                    got_promos[promo[2:]] = [ind]
                print(got_promos)

                
            elif promo == "":
                pass
            
            else:
                unicum_sheet[str(ind)+'u'].append((indx,promo))
                
                
       
        
        
        
        
    
regenerate()
