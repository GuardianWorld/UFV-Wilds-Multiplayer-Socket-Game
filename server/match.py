import random
import sys
import socket
import json
import threading
import time
import signal
import database

from config import active_connections, logged_users, stop_event, searching_for_match, match_rooms, log_event_level, delay_for_lag

def search_match():
    print("[*] Matchmaking Server Started.")
    matched_players = []
    while not stop_event.is_set():
        if(len(searching_for_match) >= 3):
            matched_players = random.sample(list(searching_for_match.items()), 3)
            player1 = matched_players[0]
            player2 = matched_players[1]
            player3 = matched_players[2]
            for player in matched_players:
                del searching_for_match[player[0]]
            match_rooms.append((player1[0], player2[0], player3[0]))                    
            # make a new thread for the match
            match_thread = threading.Thread(target=play_field, args=(player1,player2,player3))
            match_thread.start()
            matched_players.clear()
            time.sleep(0.2)
        else:
            time.sleep(3)
    print("[*] Matchmaking Server Stopped.")

def waiting_for_match(player_name, player_socket):
    searching_for_match[player_name] = player_socket
    return {"status": 200, "message": "Searching for match...", "command": "match_wait"}

def player_searching(player_name):
    if player_name in searching_for_match:
        return True
    return False

def player_in_match(player_name):
    for match in match_rooms:
        if player_name in match:
            return True
    return False

def players_info(p1,p2,p3):
    player1_id = database.get_user_id(p1[0])[0]
    player2_id = database.get_user_id(p2[0])[0]
    player3_id = database.get_user_id(p3[0])[0]    
    player1_deck = database.get_active_deck(player1_id)[0]
    player2_deck = database.get_active_deck(player2_id)[0]
    player3_deck = database.get_active_deck(player3_id)[0]
    player1_cards = [card[0] for card in database.get_cards_in_deck(player1_deck)]
    player2_cards = [card[0] for card in database.get_cards_in_deck(player2_deck)]
    player3_cards = [card[0] for card in database.get_cards_in_deck(player3_deck)]
    
    player1_hand = random.sample(player1_cards, 3)
    #pop cards from player1_cards
    player1_cards = [card for card in player1_cards if card not in player1_hand]
    player2_hand = random.sample(player2_cards, 3)
    player2_cards = [card for card in player2_cards if card not in player2_hand]
    player3_hand = random.sample(player3_cards, 3)
    player3_cards = [card for card in player3_cards if card not in player3_hand]
    
    player1 = {"name": p1[0], "socket": p1[1], "id": player1_id, "cards": player1_cards, "hand": player1_hand}
    player2 = {"name": p2[0], "socket": p2[1], "id": player2_id, "cards": player2_cards, "hand": player2_hand}
    player3 = {"name": p3[0], "socket": p3[1], "id": player3_id, "cards": player3_cards, "hand": player3_hand}
    
    return player1, player2, player3

def get_attribute(player):
    send_message(player, json.dumps({"status": 200, "message": "Select an attribute", "command": "select_attribute"}).encode())
    while True:
        try:
            request = player['socket'].recv(8192)
            data = json.loads(request.decode())
            command = data.get('command')
            if(command == "select_attribute"):
                attribute = data.get('attribute')
                if(attribute == "Forca" or
                   attribute == "Fofura" or
                   attribute == "Velocidade" or
                   attribute == "Tamanho" or
                   attribute == "Idade" or
                   attribute == "Tipo"):
                    return attribute
                else:
                    send_message(player, json.dumps({"status": 400, "message": "Invalid attribute", "command": "error"}).encode())
            else:
                send_message(player, json.dumps({"status": 400, "message": "Invalid command", "command": "error"}).encode())
        except socket.timeout:
            continue
        except Exception as e:
            print(str(e))
            return None

def get_played_card(player, attribute):
    card_hand = []
    for card_id in player['hand']:
        card = database.get_card_by_id(card_id)
        card_value = database.get_card_attribute(card_id, attribute)
        card_hand.append((card, card_value))
    try:
        send_message(player, json.dumps({"status": 200, "message": "Select a card", "command": "select_card", "hand": card_hand, "attribute": attribute}).encode())
    except Exception as e:
        print(str(e))
        return None, None
    
    while True:
        try:
            request = player['socket'].recv(8192)
            data = json.loads(request.decode())
            command = data.get('command')
            if(command == "select_card"):
                card_name = data.get('card_name')
                try:
                    card_id = database.get_card_id(card_name)[0]
                except:
                    send_message(player, json.dumps({"status": 400, "message": "Invalid card", "command": "error"}).encode())
                    continue
                
                if(card_id in player['hand']):
                    card = database.get_card_by_id(card_id)
                    break
                else:
                    send_message(player, json.dumps({"status": 400, "message": "Invalid card", "command": "error"}).encode())
            elif(command == "check_card"):
                card_name = data.get('card')
                response = database.get_card_info(data.get('card_name'))
                send_message(player, json.dumps(response).encode()) 
            else:
                send_message(player, json.dumps({"status": 400, "message": "Invalid command", "command": "error"}).encode())
        except socket.timeout:
            continue
        except Exception as e:
            print(str(e))
            return None, None
    return card, player['name']

def attribute_to_int(value, attribute):
    tamanho_dict = {1: "Minusculo", 2: "Pequeno", 3: "Medio", 4: "Grande", 5: "Enorme"}
    idade_dict = {1: "Jovem", 2: "Adolescente", 3: "Adulto", 4: "Anciao"}
    Tipo_dict = {1: "Terrestre", 2: "Voador", 3: "Aquatico"}
    
    if(attribute == "Forca"):
        return int(value)
    elif(attribute == "Fofura"):
        return int(value)
    elif(attribute == "Velocidade"):
        return int(value)
    elif(attribute == "Tamanho"):
        for key, val in tamanho_dict.items():
            if(value == val):
                return key
    elif(attribute == "Idade"):
        for key, val in idade_dict.items():
            if(value == val):
                return key
    elif(attribute == "Tipo"):
        for key, val in Tipo_dict.items():
            if(value == val):
                return key

def show_hand(player):
    card_hand = []
    for card_id in player['hand']:
        card = database.get_card_by_id(card_id)
        card_hand.append(card)
    
    cards_in_deck = len(player['cards'])
    send_message(player, json.dumps({"status": 200, "message": "Select a card", "command": "card_hand", "hand": card_hand, "cards": cards_in_deck}).encode())
    return

def normal_attributes_fight(p1, p2, p3, attribute):
    
    players = [(p1[0], attribute_to_int(p1[1], attribute)),
               (p2[0], attribute_to_int(p2[1], attribute)),
               (p3[0], attribute_to_int(p3[1], attribute))]
    
    #Get the highest value
    highest_value = max(players, key=lambda x: x[1])[1]
    highest_players = [player[0] for player in players if player[1] == highest_value]
    if len(highest_players) > 1:
        return random.choice(highest_players)
    return highest_players[0]
    

def special_attributes_fight(p1, p2, p3):
    
    hierarchy = {
        "Voador": "Terrestre",
        "Terrestre": "Aquatico",
        "Aquatico": "Voador"
    }
    
    cards = {p1[0]:p1[1], p2[0]:p2[1], p3[0]:p3[1]}
    winning_player = p1[0]
    winning_attribute = p1[1]

    for player_name, card_attribute in cards.items():
        if(winning_attribute == "Terrestre"):
            if(card_attribute == "Voador"):
                winning_player = player_name
                winning_attribute = card_attribute
        elif(winning_attribute == "Voador"):
            if(card_attribute == "Aquatico"):
                winning_player = player_name
                winning_attribute = card_attribute
        elif(winning_attribute == "Aquatico"):
            if(card_attribute == "Terrestre"):
                winning_player = player_name
                winning_attribute = card_attribute              
            
        
    
    return winning_player
            
    
          

def determine_winner(p1, p2, p3, attribute):
    p1_value = database.get_card_attribute(p1[1], attribute)[0]
    p2_value = database.get_card_attribute(p2[1], attribute)[0]
    p3_value = database.get_card_attribute(p3[1], attribute)[0]
    
    if(attribute == "Tipo"):
        return special_attributes_fight((p1[0], p1_value), (p2[0], p2_value), (p3[0], p3_value))
    else:
        return normal_attributes_fight((p1[0], p1_value), (p2[0], p2_value), (p3[0], p3_value), attribute)

def winTurn(p1_card, p2_card, p3_card, win_player, second_player, third_player):
    p1_name = win_player['name']
    win_player['cards'].append(p1_card[0])
    win_player['cards'].append(p2_card[0])
    win_player['cards'].append(p3_card[0])
    send_message(win_player, json.dumps({"status": 200, "message": "You won this turn!", "command": "turn_end", "winner": p1_name}).encode())
    send_message(second_player, json.dumps({"status": 200, "message": "You lost this turn!", "command": "turn_end", "winner": p1_name}).encode())
    send_message(third_player, json.dumps({"status": 200, "message": "You lost this turn!", "command": "turn_end", "winner": p1_name}).encode())
    
    return win_player
    

def turn(first_player, second_player, third_player):    
    
    send_message(first_player, json.dumps({"status": 200, "message": "Your turn", "command": "your_turn", "hand": first_player['hand']}).encode())
    send_message(second_player, json.dumps({"status": 200, "message": f"{first_player['name']} turn", "command": "opponent_turn", "hand": second_player['hand']}).encode())
    send_message(third_player, json.dumps({"status": 200, "message": f"{first_player['name']} turn", "command": "opponent_turn", "hand": third_player['hand']}).encode())
    
    show_hand(first_player)
    show_hand(second_player)
    show_hand(third_player)
    
    attribute = get_attribute(first_player)
    if(attribute == None):
        return None, None, None
    p1_card, p1_name = get_played_card(first_player, attribute)
    if(p1_card == None):
        return None, None, None
    p2_card, p2_name = get_played_card(second_player, attribute)
    if(p2_card == None):
        return None, None, None
    p3_card, p3_name = get_played_card(third_player, attribute)
    if(p3_card == None):
        return None, None, None
    
    winner_player = determine_winner([first_player['name'],p1_card[0]], [second_player['name'], p2_card[0]], [third_player['name'], p3_card[0]], attribute)
    # Remove cards from everyone hand
    first_player['hand'].remove(p1_card[0])
    second_player['hand'].remove(p2_card[0])
    third_player['hand'].remove(p3_card[0])
    
    if winner_player == first_player['name']:
        first_player = winTurn(p1_card, p2_card, p3_card, first_player, second_player, third_player)
    elif winner_player == second_player['name']:
        second_player = winTurn(p2_card, p1_card, p3_card, second_player, first_player, third_player)
    else:
        third_player = winTurn(p3_card, p1_card, p2_card, third_player, first_player, second_player)

    return first_player, second_player, third_player

def match_end(p1, p2, p3):
    if(len(p1['cards']) == 0 or len(p2['cards']) == 0 or len(p3['cards']) == 0):
        return True
    return False

def check_winner(player1, player2, player3):
    player1_score = len(player1['cards'])
    player2_score = len(player2['cards'])
    player3_score = len(player3['cards'])
    
    if player1_score > player2_score and player1_score > player3_score:
        return player1, player2, player3
    elif player2_score > player1_score and player2_score > player3_score:
        return player2, player1, player3
    else:
        return player3, player1, player2

def buy_cards(player):
    player['hand'].append(player['cards'][0])
    player['cards'] = player['cards'][1:]
    
    return player


def play_order(p1, p2, p3):
    first_player = random.choice([p1, p2, p3])
    second_player = None
    third_player = None
    
    if first_player['name'] == p1['name']:
        second_player = p2
        third_player = p3
    elif first_player['name'] == p2['name']:
        second_player = p1
        third_player = p3
    else:
        second_player = p1
        third_player = p2
    
    return first_player, second_player, third_player

def send_error(p1):
    try:
        p1['socket'].send(json.dumps({"status": 400, "message": "An error occurred during the match", "command": "match_end"}).encode())
    except:
        pass

def send_message(player, encoded_message):
    try:
        socket = player['socket']
        if(socket == None):
            socket = player
        socket.send(encoded_message)
    except:
        return False
    time.sleep(delay_for_lag)
    return True

def play_field(p1, p2, p3): 
    
    player1, player2, player3 = players_info(p1,p2,p3)
    first_player, second_player, third_player = play_order(player1, player2, player3)
    
    if(log_event_level >= 4):
        print(f"[*] Match started between {player1['name']}, {player2['name']} and {player3['name']}")
    
    send_message(player1, json.dumps({"status": 200, "message": "match", "command": "match_start", "player_1": player1['name'], "player_2": player2['name'], "player_3": player3['name']}).encode())
    send_message(player2, json.dumps({"status": 200, "message": "match", "command": "match_start", "player_1": player1['name'], "player_2": player2['name'], "player_3": player3['name']}).encode())
    send_message(player3, json.dumps({"status": 200, "message": "match", "command": "match_start", "player_1": player1['name'], "player_2": player2['name'], "player_3": player3['name']}).encode())
    
    should_end = False
    
    error = False
    
    while not stop_event.is_set() and not should_end:
        try:
            time.sleep(0.5)
            first_player, second_player, third_player = turn(first_player, second_player, third_player)         
            
            if(first_player == None or second_player == None or third_player == None):
                error = True
                
                break   
                
            aux_player = first_player
            first_player = second_player
            second_player = third_player
            third_player = aux_player
        
            first_player = buy_cards(first_player)
            second_player = buy_cards(second_player)
            third_player = buy_cards(third_player)
            
            should_end = match_end(first_player, second_player, third_player)
        except Exception as e:
            print(f"Error during match: {str(e)}")
            error = True
            break
    if(log_event_level >= 4):
        print("[*] Match ended.")
        
    if(error):
        send_error(player1)
        send_error(player2)
        send_error(player3)
        match_rooms.remove((player1['name'],player2['name'], player3['name']))
        return
    
    winner_player, l1, l2 = check_winner(first_player, second_player, third_player)
    
    send_message(winner_player, json.dumps({"status": 200, "message": "You won!", "command": "match_end"}).encode())
    send_message(l1, json.dumps({"status": 200, "message": "You lost!", "command": "match_end"}).encode())
    send_message(l2, json.dumps({"status": 200, "message": "You lost!", "command": "match_end"}).encode())

    full_deck = l1['cards'] + l2['cards']
    reward_card = None
    
    while True:
        try:
            reward_card = random.choice(full_deck)
            full_deck = [card for card in full_deck if card != reward_card]
            
            amount = database.get_card_amount_userID(winner_player['id'], reward_card)
            if(amount == None):
                amount = 0
            else:
                amount = amount[0]
                
            if amount < 3:
                database.add_card_to_user(winner_player['id'], reward_card)
                reward_card_name = database.get_card_by_id(reward_card)[1]
                send_message(winner_player, json.dumps({"status": 200, "message": "You won a card!", "command": "reward", "card": reward_card_name}).encode())
                break
            if len(full_deck) == 0:
                send_message(winner_player, json.dumps({"status": 200, "message": "You won a card!", "command": "reward", "card": "You have all cards on the reward table"}).encode())
                break
        except Exception as e:
            print(str(e))
            break
    
    
    first_player['socket'].settimeout(5)
    second_player['socket'].settimeout(5)
    third_player['socket'].settimeout(5)
    #remove from match_rooms
    match_rooms.remove((player1['name'],player2['name'], player3['name']))
    return