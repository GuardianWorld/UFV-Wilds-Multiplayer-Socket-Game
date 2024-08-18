import random
import sys
import json
import threading
import time
import signal
import database
import Pyro5.api

from config import stop_event, match_rooms, log_event_level, delay_for_lag

def search_match(ufv_wilds_server):
    print("[*] Matchmaking Server Started.")
    matched_players = []
    while not stop_event.is_set():
        #print(len(ufv_wilds_server.searching_for_match))            
        if(len(ufv_wilds_server.searching_for_match) >= 3):
            matched_players = random.sample(list(ufv_wilds_server.searching_for_match.items()), 3)
            player1 = matched_players[0]
            player2 = matched_players[1]
            player3 = matched_players[2]
            for player in matched_players:
                del ufv_wilds_server.searching_for_match[player[0]]
            match_rooms.append((player1[0], player2[0], player3[0]))                    
            # make a new thread for the match
            match_thread = threading.Thread(target=play_field, args=(player1,player2,player3))
            match_thread.start()
            matched_players.clear()
            time.sleep(0.2)
        else:
            time.sleep(3)
    print("[*] Matchmaking Server Stopped.")

def players_info(p1,p2,p3):
    player1_name, player1_URI = p1
    player2_name, player2_URI = p2
    player3_name, player3_URI = p3
    client1_proxy = Pyro5.api.Proxy(player1_URI)
    client2_proxy = Pyro5.api.Proxy(player2_URI)
    client3_proxy = Pyro5.api.Proxy(player3_URI)
    player1_id = database.get_user_id(player1_name)[0]
    player2_id = database.get_user_id(player2_name)[0]
    player3_id = database.get_user_id(player3_name)[0]    
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
    
    player1 = {"name": player1_name,"URI": player1_URI, "proxy": client1_proxy, "id": player1_id, "cards": player1_cards, "hand": player1_hand}
    player2 = {"name": player2_name,"URI": player2_URI, "proxy": client2_proxy, "id": player2_id, "cards": player2_cards, "hand": player2_hand}
    player3 = {"name": player3_name,"URI": player3_URI, "proxy": client3_proxy, "id": player3_id, "cards": player3_cards, "hand": player3_hand}
    
    return player1, player2, player3

def get_attribute(player):
    request = player['proxy'].select_attribute()
    try:
        if(request != "Invalid"):
            return request
    except Exception as e:
        print(str(e))
        return None

def get_played_card(player, attribute):
    response = player['proxy'].select_card(attribute)
    try:
        card_id = database.get_card_id(response)[0]
        
        if(card_id in player['hand']):
            card = database.get_card_by_id(card_id)
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
    player['proxy'].card_hand(cards_in_deck, card_hand)
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
    win_player['proxy'].turn_end(p1_name)
    second_player['proxy'].turn_end(p1_name)
    third_player['proxy'].turn_end(p1_name)
    
    return win_player
    

def turn(first_player, second_player, third_player):    
    
    first_player['proxy'].your_turn()
    second_player['proxy'].opponent_turn()
    third_player['proxy'].opponent_turn()

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
    if(len(p1['cards']) == 5 or len(p2['cards']) == 5 or len(p3['cards']) == 5):
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

def send_error(p1, URI):
    try:
        p1['proxy'].match_end(URI)
    except:
        pass

def play_field(p1, p2, p3): 
    
    player1, player2, player3 = players_info(p1,p2,p3) #oki doki
    first_player, second_player, third_player = play_order(player1, player2, player3)
    
    if(log_event_level >= 4):
        print(f"[*] Match started between {player1['name']}, {player2['name']} and {player3['name']}")
    
    player1['proxy'].match_start(player1['name'], player2['name'], player3['name'])
    player2['proxy'].match_start(player1['name'], player2['name'], player3['name'])
    player3['proxy'].match_start(player1['name'], player2['name'], player3['name'])
  
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
        send_error(player1, player1["URI"])
        send_error(player2, player2["URI"])
        send_error(player3, player3["URI"])
        match_rooms.remove((player1['name'],player2['name'], player3['name']))
        return
    
    winner_player, l1, l2 = check_winner(first_player, second_player, third_player)
    
    winner_player['proxy'].match_end()
    l1['proxy'].match_end()
    l2['proxy'].match_end()

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
                winner_player['proxy'].reward(reward_card_name)
                break
            if len(full_deck) == 0: 
                break
        except Exception as e:
            print(str(e))
            break
    
    #remove from match_rooms
    match_rooms.remove((player1['name'],player2['name'], player3['name']))
    return