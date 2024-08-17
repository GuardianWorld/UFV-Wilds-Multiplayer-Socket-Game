import base64
import select
import hashlib
import string
import threading
import json
import sys
import os
import queue
from time import sleep

import pygame
from mainTelas import startInterface
import Pyro5.api

stop_event = threading.Event()
token = ""
username = ""
login_into_server = False
searching_for_match = False
on_match = False
on_turn = False
downloading_file = False
client_id = ""


def close_connection(client_socket):
    print("[*] Disconnected from server.")
    
    client_socket.close()
    
def match_commands(message, token):
    full_message = message.split(' ', 1)
    command = full_message[0]
    json_message = {}
    send_status = True
    if(command == "select_attribute"):
        attribute = full_message[1]
        json_message = {"token": token, "message": "", "command": "select_attribute", "attribute": attribute}
    if(command == "select_card"):
        card_name = full_message[1]
        json_message = {"token": token, "message": "", "command": "select_card", "card_name": card_name}
    if(command == "forfeit"):
        json_message = {"token": token, "message": "", "command": "forfeit"}
    if(command == "check_card"):
        card_name = full_message[1]
        json_message = {"token": token, "message": "", "command": "check_card", "card_name": card_name}
    if(command == "help"):
        # print("Commands: ")
        # print("select_attribute <attribute>: Select an attribute to play")
        # print("select_card <card>: Select a card to play")
        # print("forfeit: Forfeit the match")
        # print("check_card <card_name>: Check a specific card")
        response_queue.put("Match help")
        send_status = False
        json_message = {"token": token, "message": "", "command": "chat"}
        
    return send_status, json_message
    
def common_commands(message, server):
    global token
    global username
    global client_id
    full_message = message.split(' ', 1)
    command = full_message[0]
    
    
    
    if(command == "exit"):
        json_message = {"token": token, "message": "", "command": "logoff"}
    elif(command == "register"):
        if(token):
            print("[*] Already logged in")
            return
        parts = message.split(' ', 2)
        if(len(parts) != 3):
            print("[*] Invalid input")
            return
        user = parts[1]
        password = parts[2]
        if(len(password) < 6):
            print("[*] Password too short")
            return
        
        status, answer = server.register(user, password)
        
        print(f"[*] {status}")
        print(f"[*] {answer}")
        
        return
    elif(command == "login"):
        if(token):
            print("[*] Already logged in")
            return
        parts = message.split(' ', 2)
        if(len(parts) != 3):
            print("[*] Invalid input")
            response_queue.put("Invalid Input")
            return
        user = parts[1]
        password = parts[2]
        if(len(password) < 6):
            print("[*] Password too short")
            response_queue.put("Password too short")
            return
        
        status, token = server.login(user, password, client_id)
        if(status == 200):
            print(f"[*] Logged in as {user}")
            username = user
            response_queue.put("logging in")     
        else:
            response_queue.put("Login failed")
        return
        
    elif(command == "check_cards"):
        status, cards = server.check_cards(token)
        if(status == 500):
            response_queue.put("Failed")
            return
        final_list = []
        for card in cards:
            card_name = card[0]
            amount = card[1]
            for i in range(amount):
                final_list.append([card_name, 1])
        response_queue.put(final_list)

    elif(command == "check_card"):
        card_name = full_message[1]
        status, card = server.check_card(token, card_name)
        if(status == 500):
            response_queue.put("Failed")
            return
        card_name = card[0]
        forca = card[2]
        fofura = card[3]
        velocidade = card[4]
        tamanho = card[5]
        idade = card[6]
        tipo = card[7]
        imagem = card[8]
        
        response_queue.put([card_name, forca, fofura, velocidade, tamanho, idade, tipo, imagem])        
    
    elif(command == "check_decks"):
        status, decks = server.check_decks(token)
        if(status == 500):
            response_queue.put("Failed")
            return
        response_queue.put(decks)
    
    elif(command == "check_deck"):
        deck_name = full_message[1]
        status, deck = server.check_deck(token, deck_name)
        if(status == 500):
            response_queue.put("Failed")
            return
        print(deck)
        deck_name = deck[0]
        cards = deck[1]
        active = deck[2]
        print(f"[*] Deck: {deck_name}, Active: {active}, Cards: {cards}")
        response_queue.put([deck_name, active, cards])

    elif command == "create_deck":
        deck_name = full_message[1]
        status, answer = server.create_deck(token, deck_name)
        if(status == 500):
            response_queue.put("Failed")
            return
        response_queue.put(["Deck created", deck_name])
    
    elif command == "delete_deck":
        deck_name = full_message[1]
        status, answer = server.delete_deck(token, deck_name)
        if(status == 500):
            response_queue.put("Failed")
            return
        response_queue.put(["Deck deleted", deck_name])
        
    elif(command == "activate_deck"):
        deck_name = full_message[1]
        status, answer = server.activate_deck(token, deck_name)
        if(status == 500):
            response_queue.put("Failed")
            return
        response_queue.put(["Activated deck", deck_name])
        
    elif(command == "add_card_to_deck"):
        parts = message.split(' ', 2)
        if(len(parts) != 3):
            response_queue.put("Invalid input")
            return
        deck_name = parts[1]
        card_name = parts[2]
        status, answer = server.add_card_to_deck(token, deck_name, card_name)
        if(status == 500):
            response_queue.put("Failed")
            return
        response_queue.put("Card added")
        
    elif(command == "remove_card_from_deck"):
        parts = message.split(' ', 2)
        if(len(parts) != 3):
            response_queue.put("Invalid input")
            return
        deck_name = parts[1]
        card_name = parts[2]
        status, answer = server.remove_card_from_deck(token, deck_name, card_name)
        if(status == 500):
            response_queue.put("Failed")
            return
        response_queue.put(["Card removed", card_name, deck_name])
        
    elif(command == "match_search"):
        send_status, json_message = match_search(token)  
        
        

def package_message(message, server, token="none"):
    global searching_for_match
    global on_match

    try:
        if(on_match):
            match_commands(message, server)
        else:
            common_commands(message, server)
    except Exception as e:
        print(f"[*] Package Exception: {str(e)}")
        response_queue.put(["Package exception", str(e)])
    
    return

def receive_message(client_socket):
    global stop_event
    global username
    global token
    global on_match
    global login_into_server
    global searching_for_match
    
    response_json = {}
    data = b""
    while not stop_event.is_set():
        try:
            response = client_socket.recv(8192)
            if not response:
                continue

            data += response
            try:
                response_json = json.loads(data.decode())
            except json.JSONDecodeError:
                continue
            
            data = b""
            
            #response_json = json.loads(response)
            if(response_json == None):
                print(f"[*] Empty Packet")
                response_queue.put("Empty packet")
                continue
            
            print("recebido:", response_json)
            message = response_json.get('message')
            command = response_json.get('command')

            # print(str(response_json))
            # print(message)
            # print(command)
            
            # print(f"[*] Received: {response_json}")
            if(command == "ping"):
                continue

            elif(command == "login"):
                token = response_json.get('token')
                username = response_json.get('username')
                login_operation(client_socket)
                
            
            elif(command == "logoff"):
                print(f"[*] Turning off")
                response_queue.put("Turning off")
                sleep(0.5)
                stop_event.set()
                return
            
            elif(command == "serverside_logoff"):
                reason = response_json.get('message')
                print(f"[*] You have been disconnected from the server.")
                # print(f"[*] Reason: {reason}")
                response_queue.put(["You have been disconnected", reason])
                sleep(1)
                stop_event.set()
                return
            
            elif(command == "check_card"):
                card_name = response_json.get('card_name')
                forca = response_json.get('forca')
                fofura = response_json.get('fofura')
                velocidade = response_json.get('velocidade')
                tamanho = response_json.get('tamanho')
                idade = response_json.get('idade')
                tipo = response_json.get('tipo')
                imagem = response_json.get('imagem')
                # print(" > Card: ", card_name)
                # print(" > Forca: ", forca)
                # print(" > Fofura: ", fofura)
                # print(" > Velocidade: ", velocidade)
                # print(" > Tamanho: ", tamanho)
                # print(" > Idade: ", idade)
                # print(" > Tipo: ", tipo)
                # print(" > Imagem: ", imagem)
                response_queue.put([card_name, forca, fofura, velocidade, tamanho, idade, tipo, imagem])
            
            elif(command == "check_cards"):
                # cards = response_json.get('cards')
                # for card in cards:
                    # print(f"[*] Card: {card[0]} Amount: {card[1]}")
                response_queue.put(response_json.get('cards'))
            
            elif(command == "create_deck"):
                deck_name = response_json.get('deck_name')
                # print(f"[*] Deck {deck_name} created")
                response_queue.put(["Deck created", deck_name])
            
            elif(command == "delete_deck"):
                deck_name = response_json.get('deck_name')
                # print(f"[*] Deck {deck_name} deleted")
                response_queue.put(["Deck deleted", deck_name])
            
            elif(command == "check_decks"):
                # decks = response_json.get('decks')
                # for deck in decks:
                    # grab out the ID, Name, User ID, Active and default
                    # deck_id, deck_name, user_id, active, default = deck
                    # if(active == 1):
                    #     active = "Yes"
                    # else:
                    #     active = "No"
                    # if(default == 1):
                    #     default = "Yes"
                    # else:
                    #     default = "No"
                    # print(f"[*] Deck Name: {deck_name}, Active: {active}, Default: {default}")
                response_queue.put(response_json.get('decks'))

            elif(command == "check_deck"):
                deck_name = response_json.get('deck_name')
                cards = response_json.get('cards')
                active = response_json.get('active')
                
                # print(f"[*] Deck: {deck}, Active: {active}")
                # for card in cards:
                #     print(f"[*] Card: {card}")
                response_queue.put([deck_name, active, cards])
            
            elif(command == "activate_deck"):
                deck_name = response_json.get('deck_name')
                # print(f"[*] Deck {deck_name} activated")
                response_queue.put(["Activated deck", deck_name])
                
            elif(command == "add_card_to_deck"):
                card_name = response_json.get('card_name')
                deck_name = response_json.get('deck_name')
                # print(f"[*] Card {card_name} added to deck {deck_name}")
                response_queue.put("Card added", card_name, deck_name)
                
            elif(command == "remove_card_from_deck"):
                card_name = response_json.get('card_name')
                deck_name = response_json.get('deck_name')
                # print(f"[*] Card {card_name} removed from deck {deck_name}")
                response_queue.put(["Card removed", card_name, deck_name])
                
            #Match Commands    
            elif(command == "match_start"):
                searching_for_match = False
                player_1 = response_json.get('player_1')
                player_2 = response_json.get('player_2')
                player_3 = response_json.get('player_3')
                # print("\n")
                # print(f"[*] Match started between {player_1}, {player_2} and {player_3}")
                response_queue.put(["Match started", player_1, player_2, player_3])
                on_match = True
            elif(command == "match_end"):
                on_match = False
                # print(f"[*] Match ended.")
                # print(f"[*] {message}")
                response_queue.put("Match ended")
            elif(command == "error"):
                # print(f"[*] Error: {message}")
                response_queue.put(["Error", message])
            elif(command == "select_attribute"):
                # print(f"[*] Select a attribute")
                # print(f"[*] Attributes: Forca, Fofura, Velocidade, Tamanho, Idade, Tipo")
                response_queue.put("Select attribute")
            elif(command == "select_card"):
                attribute_in_play = response_json.get('attribute')
                hand = response_json.get('hand')
                # print(f"[*] Select a card")
                # print(f"[*] Attribute in play: {attribute_in_play}")
                response_queue.put("Select card")
                response_queue.put(attribute_in_play)
                # x = 0
                # for card, card_value in hand:
                #     print(f"[*] Card: {card[1]} Value: {card_value}")
                #     x += 1
            elif(command == "your_turn"):
                # print(f"[*] Your turn")
                response_queue.put("Your turn")
            elif(command == "opponent_turn"):
                # print(f"[*] Opponent turn")
                response_queue.put("Opponent turn")
            elif(command == "turn_end"):
                winner = response_json.get('winner')
                # print(f"[*] Turn ended")
                # print(f"[*] Winner: {winner}")
                # print(f"[*] {message}")
                response_queue.put(["Turn ended", winner])
                
            elif(command == "reward"):
                reward = response_json.get('card')
                # print(f"[*] Reward: {response_json.get('card')}") 
                response_queue.put(reward)
            elif(command == "card_hand"):
                hand = response_json.get('hand')  
                cards = response_json.get('cards')
                # print(f"[*] Remaining in deck: {cards}")
                # for card in hand:
                #     print(f"[*] Card: {card[1]}")
                response_queue.put([cards, hand])
            elif(command == "msg"):                    
                sender = response_json.get('sender')
                message = response_json.get('message')
                if(sender != username):
                    # print(f"\n[*] Message from {sender}: {message}")
                    response_queue.put(["Message from", sender, message])
            else:
                # print(f"[*] Message: {message}")    
                response_queue.put(["Message", message])
        except KeyboardInterrupt:
            # print("\n[*] User interruption.")
            response_queue.put("User interruption")
            stop_event.set()
            exit(0)
        except Exception as e:
            # print(f"[*] Receive Exception: {str(e)}")\
            response_queue.put(["Receive exception", str(e)])
            sleep(4)
            stop_event.set()
            return

def match_handler(client_socket):
    global on_match
    global on_turn
    while not stop_event.is_set() and on_match:
        pass 

def heartbeats():
    ns = Pyro5.api.locate_ns()                           
    uri = ns.lookup("ufv_wilds.server")            
    server = Pyro5.api.Proxy(uri)                         
    global stop_event
    global client_id
    while not stop_event.is_set():
        try:
            server.update_heartbeat(client_id)
            sleep(5)
        except Exception as e:
            print(f"[*] Heartbeat Exception: {str(e)}")
            return
    
#Start Client
def start_client(host, port):
    print("[*] Starting Up... Please wait...")
    ns = Pyro5.api.locate_ns()                           
    uri = ns.lookup("ufv_wilds.server")             
    server = Pyro5.api.Proxy(uri)    
    
    global stop_event
    global token
    global username
    global login_into_server
    global on_match
    global client_id         
    global message_queue
    global response_queue   
    
    client_id = server.set_connection()
    if(not client_id):
        stop_event.set()
        return

    print(f"[*] Connected to the server.")
    print(f"[*] Client ID: {client_id}", flush=True)
        
    file_checking(server, client_id)    
    
    heartbeats_thread = threading.Thread(target=heartbeats)
    heartbeats_thread.start()
                  
    ui_thread = threading.Thread(target=startInterface, args=(message_queue, response_queue))
    ui_thread.start()
          
    try:
        while not stop_event.is_set():
            if(on_match):
                match_handler(server)
                sleep(1)
                continue
            if not message_queue.empty():
                message = message_queue.get()
                print("enviado:", message)
                if(message == "exit"):
                    stop_event.set()
                    break
                package_message(message, server, token)
                sleep(0.25)
    except KeyboardInterrupt:
        print("\n[*] User interruption.")
        stop_event.set()
        exit(0)
        return
    except Exception as e:
        print(f"[*] Sender Exception: {str(e)}")
        response_queue.put(["Sender excepiton", str(e)])
        return
    
    heartbeats_thread.join()

        
# Aux Functions

def file_checking(server, client_id):
    print(f"[*] Loading... Please wait ")
    
    file_list = server.get_file_list(client_id)
    print(f"[*] There exists {len(file_list)} files.")
    amount, missing_indexes = verify_files(file_list)
    
    if(amount == 0):
        print("[*] All files are up to date.")
    else:
        print(f"[*] Missing {amount} files.")
        sleep(1)
    
    for index in missing_indexes:
        file = file_list[index]
        path = os.path.join(os.getcwd(), "StreamingAssets", file[0])
        print(f"[*] Requesting file: {file[0]}")
        b64_file = server.request_file(client_id, file[0])
        b64_to_image(b64_file, path)
        sleep(0.2)
        
    
    
        

def match_search(token):
    
    if(not token):
        return False, {"token": token, "message": "Not logged in", "command": "error"}
    global searching_for_match
    if(searching_for_match):
        return False, {"token": token, "message": "Already searching for match", "command": "error"}
    searching_for_match = True
    return True, {"token": token, "message": "Match Search", "command": "match_search"} 

def delete_deck(message, token):
    if(not token):
        return False, {"token": token, "message": "Not logged in", "command": "error"}
    
    parts = message.split(' ', 2)
    if(len(parts) != 2):
        return False, {"token": token, "message": "Invalid input", "command": "error"}
    
    deck_name = parts[1]
    return True, {"token": token, "message": "Deleting deck", "command": "delete_deck", "deck_name": deck_name}    

def add_card_to_deck(message, token):
    if(not token):
        return False, {"token": token, "message": "Not logged in", "command": "error"}
    
    parts = message.split(' ', 2)

    if(len(parts) != 3):
        return False, {"token": token, "message": "Invalid input", "command": "error"}
    
    deck_name = parts[1]
    card_name = parts[2]
    
    return True, {"token": token, "message": "Adding card to deck", "command": "add_card_to_deck", "deck_name": deck_name, "card_name": card_name}

def remove_card_from_deck(message, token):
    if(not token):
        return False, {"token": token, "message": "Not logged in", "command": "error"}
    
    parts = message.split(' ', 2)
    if(len(parts) != 3):
        return False, {"token": token, "message": "Invalid input", "command": "error"}
    
    deck_name = parts[1]
    card_name = parts[2]
    
    return True, {"token": token, "message": "Removing card from deck", "command": "remove_card_from_deck", "deck_name": deck_name, "card_name": card_name}
                      
def download_files(client_socket, missing_indexes, amount, server_files, token):
    x = 0
    for index in missing_indexes:
        file = server_files[index]

        package = json.dumps({"token": token, "message": "", "command": "download_images", "image_path": file[0]})
        client_socket.send(package.encode())
        print(f"[*] Requesting file: {file[0]} {x} / {amount}")

        try:
            data = b""
            while True:
                part = client_socket.recv(8192) 
                if not part:
                    break
                data += part
                try:
                    file_data_json = json.loads(data.decode())
                    break
                except json.JSONDecodeError:
                    continue 
            if file_data_json.get('command') == "file_download":
                path = os.path.join(os.getcwd(), "StreamingAssets", file[0])
                if os.name == 'nt':
                    path = path.replace("/", "\\")
                imageb64 = file_data_json.get('imageb64')
                b64_to_image(imageb64, path)
                # print(f"[*] File {path} downloaded.")
                x += 1
        except Exception as e:
            # print(f"[*] Download Exception: {str(e)}")
            response_queue.put(["Download exception", str(e)])
            break
                    
def verify_files(server_files):    
    missing_indexes = []
    missing_files = 0
    files = list_files("StreamingAssets")
    files_checksum = []
    
    for file in files:
        path = os.getcwd() + "/StreamingAssets/" + file
        if(os.name == 'nt'):
            path = path.replace("/", "\\")
        files_checksum.append(calculate_checksum(path))        

    for file in server_files:
        file_name = file[0]
        if file_name not in files:
            missing_files += 1
            missing_indexes.append(server_files.index(file))
            # print(f"[*] Missing file: {file_name}")
            response_queue.put(["Missing file", file_name])
        else:
            server_file_checksum = file[1]
            #check the checksum
            if(server_file_checksum not in files_checksum):
                missing_indexes.append(server_files.index(file))
                missing_files += 1
                # print(f"[*] File {file_name} is outdated or corrupted.")
                response_queue.put(["File outdated or corrupted.", file_name])

    return missing_files, missing_indexes


#Image functions
def b64_to_image(b64_string, image_path):
    with open(image_path, "wb") as file:
        file.write(base64.b64decode(b64_string))

#Grab all images in /StreamingAssets Folder

def directory_maker(directory="StreamingAssets"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    elif not os.path.isdir(directory):
        os.remove(directory)
        os.makedirs(directory)
        
def calculate_checksum(file_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def list_files(directory):  
    files = []
    for item in os.listdir(directory):
        file_path = os.path.join(directory, item)
        if os.path.isfile(file_path):
            files.append(item)
    return files

def offline_commands():
    while True:
        offline_command = input("Enter 'exit' to close the client or 'start' to start the connection: ")
        if(offline_command == "exit"):
            return False
        if(offline_command == "start"):
            return True

if __name__ == "__main__":
    global message_queue
    global response_queue

    message_queue = queue.Queue()
    response_queue = queue.Queue()

    host = "localhost"
    port = 25555
    if(len(sys.argv) == 3):
        host = sys.argv[1]
        port = int(sys.argv[2])
    # start = offline_commands()
    start = True
    if(start):
        directory_maker()
        start_client(host, port)
