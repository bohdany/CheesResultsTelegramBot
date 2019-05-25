'''
    v1.1
    1. Два одинакові прізвища не приходять Фарович. Це очікувано, треба писати прізвище та імя.
    2. Fixed.   ----->>>>>    Хочуть результати після закінчення туру.
    3. Fixed.   ----->>>>>    Кидає сміття у список учасників print(list_player_name) 
    4. Fixed.   ----->>>>>    Пережеребкування
    5. Правила для нових користувачів
    6. Для кожного абонента результат на одне і те саме прізвище.
    
    v1.2
    1.
    2.
'''
import time
import re
import telepot
from bs4 import BeautifulSoup
import requests
import logging
import random

# Telegram token
token = '679173797:AAGpH7YbB19_j_eo5-yV_0dPv6AK9KjmWw8'
TelegramBot = telepot.Bot(token)


REFRESH_TIME_SECONDS         = 80
START_TOURNAMENT_ID_OFFSET   = 12
END_TOURNAMENT_ID_OFFSET     = 18
PROCESS_NUMBER_OF_TORNAMENTS = 4

round_count      = 0
tmp_count        = 0
player_db        = []
number_tours_db  = []
num_board_db     = []
current_score_db = []
send_warning_db  = ['0']
send_welcome_db  = ['0']


# Verify if player and his tour id if not in database add it. If player and tour id is in db return and don't send message
def verify_registrate_in_db(player_name, number_tours, board, current_score, final_score):

    print('+++')
    print(player_db)
    print(number_tours_db)
    print(num_board_db)
    print('+++')
    
    if number_tours == 0:
        return False
    
    is_flag = False
    for index in range(len(player_db)):
        if(player_db[index] == player_name):
            is_flag = True
            if (number_tours_db[index] == number_tours):
                return False
            elif (number_tours_db[index] != number_tours) or (num_board_db[index] != board) or (current_score_db[index] != current_score):
                number_tours_db[index] = number_tours
                return True
                
    if is_flag == False:
        player_db.append(player_name)
        number_tours_db.append(number_tours)
        num_board_db.append(board)
        current_score_db.append(current_score)
        return True

# Convert raw aspx page to line by line array   
def final_results_database_line_by_line(final_results_database):
    line_by_line = []
    pos1=0
    while pos1>=0:
        pos1 = final_results_database.find('<tr class="CRg', pos1+50)
        pos2 = final_results_database.find('</tr>', pos1)
        line_by_line.append(final_results_database[pos1:pos2])
    
    return line_by_line    
        

# Filter out string from tags artifacts
def filter_out_string(string):
    pos1=0
    pos2=0
    list_item = []
    while pos2 > -1:
        pos1 = string.find('>', pos2)
        pos2 = string.find('<', pos1)
        if string[pos1+1:pos2] and string[pos1+1:pos2] != '' and string[pos1+1:pos2] != ' ':
            list_item.append(string[pos1+1:pos2])
            
    pos1=0
    pos2=0
    list_item2 = []
    while pos2 > -1:
        pos1 = string.find('>', pos2)
        pos2 = string.find('<', pos1)
        if string[pos1+1:pos2] and string[pos1+1:pos2] != ' ' and string[pos1+1:pos2] != 'GM'and string[pos1+1:pos2] != 'IM' and string[pos1+1:pos2] != 'FM' and string[pos1+1:pos2] != 'CM' and string[pos1+1:pos2] != 'WGM'and string[pos1+1:pos2] != 'WIM' and string[pos1+1:pos2] != 'WFM' and string[pos1+1:pos2] != 'WCM' and string[pos1+1:pos2] != 'I' and string[pos1+1:pos2] != 'II' and string[pos1+1:pos2] != 'III' and string[pos1+1:pos2] != 'U10' and string[pos1+1:pos2] != 'U16':
            for each in string[pos1+1:pos2]:
                if each.isalpha():
                    list_item2.append(string[pos1+1:pos2])
                    break
    
    # Scores
    pos1=0
    pos2=0
    list_item4 = ' '
    while pos2 > -1:
        pos1 = string.find('>', pos2)
        pos2 = string.find('<', pos1)
        if string[pos1+1:pos2].find(' - ') > 0:
            list_item4 = str(string[pos1+1:pos2])
        
    board         = list_item[0]
    player1       = list_item2[0]
    player2       = list_item2[1]
    current_score = list_item4
    final_score   = 0
    
    return board, player1, player2, current_score, final_score

# Execute this loop with Refresh Rate = REFRESH_TIME_SECONDS
while True:

    try:    
        # Look for latest tournament
        url = 'http://chess-results.com/fed.aspx?lan=1&fed=UKR'
        url_get = requests.get(url)
        content = str(BeautifulSoup(url_get.content, 'lxml'))
        
        position_first_tournament = 0
        for tournament in range(PROCESS_NUMBER_OF_TORNAMENTS):
            # Look for latest updated tournament
            position_first_tournament = content.find('<a href="tnr', position_first_tournament+10)
            first_tournament_id = content[position_first_tournament+START_TOURNAMENT_ID_OFFSET:position_first_tournament+END_TOURNAMENT_ID_OFFSET]
            
            # Uncomment this line ------> 
            first_tournament_url = str('http://chess-results.com/tnr') + str(first_tournament_id) + str('.aspx')
            #first_tournament_url = 'http://chess-results.com/tnr386561.aspx'
            
            # Look for latest round
            url = first_tournament_url + str('?lan=1&art=2')
            url_get = requests.get(url)
            final_results_database = str(BeautifulSoup(url_get.content, 'lxml'))
            
            try:
                pos2 = 0
                count = 50
                while count:
                    # Count number of started tours
                    pos1 = final_results_database.find('>Rd.', pos2)
                    pos2 = final_results_database.find('<', pos1)
                    temp = final_results_database[pos1:pos2]
                    count -= True
                    if  temp.find('/') > 0:
                        pos1 = temp.find('.')
                        pos2 = temp.find('/', pos1)
                        number_tours = int(temp[pos1+1:pos2])
                        break
                    if count == 1:
                        number_tours = 0
                        
            except:
                number_tours = 0
                pass
                
            # Convert raw array to line by line for easy parsing
            line_by_line = final_results_database_line_by_line(final_results_database)
                    
            # Get list of recievers
            list_user_id     = []
            list_player_name = []
            updates = TelegramBot.getUpdates(token)
            for item in updates:
                item    = str(item)
                pos1 = item.find("'id':")
                pos2 = item.find(",", pos1)
                user_id     = item[pos1+6:pos2]
                
                pos1 = item.find("'text': '")
                pos2 = item.find("'", pos1+9)                
                player_name = item[pos1+9:pos2]
                
                found_flag1 = False
                found_flag2 = False
                # Verify if string contain first and second name
                if str(player_name).find(' ') > 0:                    
                    list_user_id.append(str(user_id))
                    list_player_name.append(str(player_name))
                elif (str(player_name).find(' ') < 0) and (str(player_name).find('start') < 0):
                    for each in send_warning_db:
                        if each.find(str(user_id)) >= 0:
                            found_flag1 = True
                    if  found_flag1 != True:
                        TelegramBot.sendMessage(str(user_id), "Запит не прийнято. Введіть прізвище та ім'я.")
                    send_warning_db.append(str(user_id))
                    
                if str(player_name).find('start') >= 0:                        
                    for each in send_welcome_db:
                        if each.find(str(user_id)) >= 0:
                            found_flag2 = True
                    if  found_flag2 != True:
                        pass
                        #TelegramBot.sendMessage(str(user_id), "1. 2. 3.")
                    send_welcome_db.append(str(user_id))
                
            print(list_player_name)                
            
            # Find name of player in latest round
            for index in range(len(list_user_id)):
                for line in line_by_line:
                    if(line.find(list_player_name[index])>=0):
                        board, player1, player2, current_score, final_score = filter_out_string(line)
                        if verify_registrate_in_db(list_player_name[index], number_tours, board, current_score, final_score):
                            TelegramBot.sendMessage(str(list_user_id[index]), 'Тур:'+str(number_tours)+'  Cтіл:'+board+'  ♘'+player1+' '+current_score+'   ♞'+player2)                    
                            break
            round_count = number_tours                    
            
            # For debug to know if script is alive
            print(tmp_count)
            tmp_count+=True
        time.sleep(random.randint(15,REFRESH_TIME_SECONDS))
    
    except:
        pass
        time.sleep(REFRESH_TIME_SECONDS*2)
        logging.exception('Exceprion occured')
        
        


    
    

