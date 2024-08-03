from os import getcwd
import argparse
import random
import sys
import socket
import json
import threading
import time
import datetime
import signal
import hashlib
import base64
import os


import database
from config import active_connections, stop_event, logged_users, searching_for_match, match_rooms, log_event_level
import match

files = []

#Signal Handling
def signal_handler(sig, frame):
    print(f"[*] Signal received: {sig}. Shutting down...")
    shutdown_server(5)

signal.signal(signal.SIGTERM, signal_handler)

#Start Server
def start_server(host, port):

    print("[*] Starting server...")
    print("[*] Loading StreamingAssets...")
    time.sleep(1)
    list_files(getcwd() + "/StreamingAssets")
    print("[*] StreamingAssets loaded.")
    
    if(log_event_level >= 5):
        print("[*] StreamingAssets: ")
        for file in files:
            print(f" > {file[0]} - Checksum: {file[1]}")
        
    #Open DB
    print("[*] Initializing database...")
    database.init_db()
    
    #Open connection
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)
        server_socket.settimeout(5.0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
 
    print("[*] Server started.")
    print(f"[*] Listening on {host}:{port}")
    print(f"[*] Log Level: {log_event_level}")  

    terminal = threading.Thread(target=internal_server_terminal)
    terminal.start()
    
    match_thread = threading.Thread(target=match.search_match)
    match_thread.start()
    
    
    while not stop_event.is_set():
        try:
            client_socket, client_address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address,))
            client_handler.start()
        except socket.timeout:
            continue
    
    terminal.join()
    match_thread.join()
    shutdown_server(1)
    server_socket.close()

#Shutdown Server
def shutdown_server(timeout=5):
    print(f"[*] Shutting down server in {timeout} seconds.")
    stop_event.set()
    time.sleep(timeout)
    for _, client_socket, _ in active_connections.items():
        client_socket.send(json.dumps({"status": 200, "message": "Server is shutting down.", "command": "serverside_logoff"}).encode())
        client_socket.close()
    sys.exit(0)

# region Internal Server Terminal

def internal_server_terminal():
    global log_event_level
    print("[*] Server terminal started.")
    while not stop_event.is_set():
        try:
            command = input(" >> ")
            if command == "shutdown":
                print("[*] Shutdown command issued, stopping...")
                stop_event.set()
            elif command == "status":
                terminal_status()
            elif command == "statistics":
                terminal_stats()
            elif command == "connections":
                terminal_comms()
            elif command == "users":
                terminal_users()
            elif command == "matches":
                terminal_matches()
            elif command == "searching":
                terminal_searching()
            elif command == "database search":
                terminal_search()
            elif command == "config":
                terminal_config() 
            elif command == "kick":
                terminal_kick()    
            elif command == "ban":
                terminal_user_ban()      
            elif command == "delete user":
                terminal_delete_user()
            elif command == "help":
                print("[*] Available commands: ")
                print(" >> shutdown - Stops the server.")
                print(" >> status - Shows server status.")
                print(" >> statistics - Shows server statistics.")
                print(" >> connections - Shows active connections.")
                print(" >> users - Shows online users.")
                print(" >> matches - Shows current matches.")
                print(" >> searching - Shows users searching for match.")
                print(" >> database search - Search the database for information.")
                print(" >> config - Shows server configuration.")
                print(" >> kick - Kicks a user.")
                print(" >> ban - Ban/Unbans a user.")
                print(" >> delete user - Deletes a user.")
                print(" >> help - Shows this message.")
            else:
                print("[*] Invalid command. Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\n[*] Keyboard interruption.")
        except Exception as e:
            print(f"Error: {e}")

    print("[*] Server terminal stopped.")

def terminal_config():
    global log_event_level
    print("[*] Configuring server.")
    command = ""
    
    while(command != "exit"):
        print("[*] Available commands: ")
        print(f" >> log level - Sets the log level. Current: {log_event_level}")
        print(" >> add card - Adds a card to the database.")
        print(" >> add test cards - Adds test cards to the database.")
        print(" >> delete card - Deletes a card from the database.")
        print(" >> check card - Checks a card in the database.")
        print(" >> all cards - Shows all cards in the database.")
        print(" >> exit - Exits configuration.")
        command = input("[config] >> ")
        print("")
        if(command == "log level"):
            print("    > 0 - No logs.")
            print("    > 1 - Player Logins")
            print("    > 2 - Player Logins + Register")
            print("    > 3 - Player Logins + Register + Matches")
            print("    > 4 - Player Logins + Register + Matches + Connections")
            print("    > 5 - Player Logins + Register + Matches + Connections + Debug")
            try:
                log_event_level = int(input("Log Level: "))
            except:
                print("[config] Invalid log level.")
        elif(command == "add card"):
            add_cards()
        elif(command == "add test cards"):
            value = int(input("[config] > Number of test cards: "))
            for i in range(value):
                add_test_cards()
        elif(command == "delete card"):
            delete_card()
        elif(command == "check card"):
            search_card()
        elif(command == "all cards"):
            all_cards()

def terminal_status():
    number_of_sockets = len(active_connections)
    print("[*] Server is running.")
    print(f"[*] Number of sockets open: {number_of_sockets}")
    print(f"[*] Number of users online: {len(logged_users)}")
    print(f"[*] Number of match rooms: {len(match_rooms)}")
    print(f"[*] Searching for match: {len(searching_for_match)}")

def terminal_stats():
    print(f"[*] Number of Users: {database.get_statistics_user()[0]}")
    print(f"[*] Number of Cards: {database.get_statistics_cards()[0]}")
    print(f"[*] Number of Decks: {database.get_statistics_decks()[0]}")
    print(f"[*] Number of Matches: {database.get_statistics_matches()[0]}")
    print(f"[*] Number of Banned Users: {database.get_statistics_banned()[0]}")   

def terminal_comms():
    print(f"[*] Active connections: ")
    for connection, socket_time_pair in active_connections.items():
        print(f" -> {connection[0]}:{connection[1]} - {socket_time_pair[1]}")

def terminal_users():
    number_of_logged_users = len(logged_users)
    number_of_users = database.get_statistics_user()[0]
    print("[*] Number of Users: ", number_of_users)
    print("[*] Number of Users Online: ", number_of_logged_users)
    print("[*] Show online users? [y/n]: ")
    value = input("[users] >> ")
    if(value == "y"):
        print("[*] Online users:")
        for connection, user in logged_users.items():
            print(f" -> {connection[0]}:{connection[1]} [{user}]")
        if(number_of_logged_users == 0):
            print(" -> No users online.")
    print("[*] Show all users? [y/n]: ")
    value = input("[users] >> ")
    if(value == "y"):
        print("[*] All users:")
        users = database.get_all_usernames()
        x = 0
        for user in users:
            x += 1
            print(f" {x} -> {user[0]}")

def terminal_matches():
    print(f"[*] Number of match rooms: {len(match_rooms)}")
    for room, players in match_rooms.items():
        print(f" -> Room {room}: {players}")

def terminal_searching():
    print(f"[*] Searching for match: {len(searching_for_match)}")
    for player, player_socket in searching_for_match.items():
        print(f" -> {player}")

def terminal_search():
    print("[*] Available search commands: ")
    command = ""
    
    while(command != "exit"):
        print(" > card - Search for cards.")
        print(" > user - Search for users.")
        print(" > exit - Exit search.")
        command = input("[search] >> ")
        if(command == "card"):
            search_card()
        elif(command == "user"):
            search_user()
        elif(command == "all_cards"):
            all_cards()
        elif(command == "all_users"):
            all_users()

def terminal_delete_user():
    print("[*] Delete a user by username.")
    username = input("[delete user] >> ")
    user = database.get_user(username)
    if(user):
        print(f"User: {user}")
        print("Delete user? [y/n]")
        confirm = input("[delete user] >> ")
        if(confirm == "y"):
            database.delete_user(username)
            print("User deleted.")
            return
        print("User not deleted.")
        return
    else:
        print("User not found.")
  
def search_card():
    print("[*] Search for cards by name.")
    card_name = input("[search card] >> ")
    card = database.get_card_by_name(card_name)
    if(card):
        card_name = card[1]
        forca =     card[2]
        fofura =    card[3]
        velocidade =card[4]
        tamanho =   card[5]
        idade =     card[6]
        tipo =      card[7]
        card_group =card[8]
        card_image =card[9]
        
        print(f"Card: {card_name}")
        print(f"Grupo: {card_group}")
        print(f"Força: {forca}")
        print(f"Fofura: {fofura}")
        print(f"Velocidade: {velocidade}")
        print(f"Tamanho: {tamanho}")
        print(f"Idade: {idade}")
        print(f"Tipo: {tipo}")
        print(f"Imagem: {card_image}")

    else:
        print("Card not found.")    
        
def all_cards():
    print("[*] All cards.")
    cards = database.get_all_cards()
    for card in cards:
        card_name = card[1]
        card_group =card[2]
        forca =     card[3]
        fofura =    card[4]
        velocidade =card[5]
        tamanho =   card[6]
        idade =     card[7]
        tipo =      card[8]
        card_image =card[9]
        
        print(f"Card: {card_name}")
        print(f"Grupo: {card_group}")
        print(f"Força: {forca}")
        print(f"Fofura: {fofura}")
        print(f"Velocidade: {velocidade}")
        print(f"Tamanho: {tamanho}")
        print(f"Idade: {idade}")
        print(f"Tipo: {tipo}")
        print(f"Imagem: {card_image}")
        print("")

def search_user():
    print("[*] Search for player information by username.")
    username = input("[search user] >> ")
    user = database.get_user(username)
    
    if(user):
        print(f"ID: {user[0]}")
        print(f"Username: {user[1]}")
        print(f"Matches Played: {user[2]}")
        print(f"Matches Won: {user[3]}")
        if(user[4] == 1):
            print(f"Banned status: Banned")
        else:
            print(f"Banned status: Not Banned")
    else:
        print("User not found.")

def all_users():
    print("[*] All users.")
    users = database.get_all_users()
    for user in users:
        print(f" >> {user}")

def terminal_user_ban():
    print("[*] Ban/Unban a user via Username.")
    username = input("[ban] >> ")
    user = database.get_user(username)
    is_banned = database.is_banned(username)
    if(user):
        if(is_banned):
            print(f"User {username} is banned.")
            print(f"Unban user {username}? [y/n]")
            print("[ban] >> ")
            confirm = input()
            if(confirm == "y"):
                database.unban_user(username)
                print(f"User {username} unbanned.")
                return
        else:
            print(f"User {username} is not banned.")
            print(f"Ban user {username}? [y/n]")
            confirm = input("[ban] >> ")
            if(confirm == "y"):
                database.ban_user(username)
                print(f"User {username} banned.")
                return
    else:
        print("User not found.")
    
    print("Operation canceled.")

def terminal_kick():
    print("[*] Disconnects a user by username.")
    username = input("[kick] >> Username: ")
    reason = input("[kick] >> Reason: ")
    
    for client_address, user in logged_users.items():
        if user == username:
            client_socket = (active_connections[client_address])[0]
            
            client_socket.send(json.dumps({"status": 200, "message": reason, "command": "serverside_logoff"}).encode())
            return
    

#endregion

#Server-Client Side

def handle_client(client_socket, client_address):     
    global log_event_level   
    if(log_event_level >= 4):
        print(f"[*] Accepted connection from: {client_address[0]}:{client_address[1]}")
    active_connections[client_address] = (client_socket, datetime.datetime.utcnow())
    if not client_socket:
        return
    
    forced_logoff_timer = 60
    
    client_socket.settimeout(5.0)
    
    
    
    try:
        while not stop_event.is_set():
            try:
                if(client_address in logged_users):
                    if(match.player_in_match(logged_users[client_address])):
                        time.sleep(1)
                        continue
                        
                request = client_socket.recv(4096)
                if not request:
                    break
                data = json.loads(request.decode())
                response = handle_response(data, client_address, client_socket)
                response_json = json.dumps(response)      
                          
                client_socket.send(response_json.encode())
                forced_logoff_timer = 60
            except socket.timeout:
                forced_logoff_timer -= 1
                if(forced_logoff_timer <= 0):
                    client_socket.send(json.dumps({"status": 200, "message": "Inactivity", "command": "serverside_logoff"}).encode())
                continue
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        del active_connections[client_address]
        if client_address in logged_users:
            #grab username
            username = logged_users[client_address]
            #delete from searched matches
            if(match.player_searching(username)):
                del searching_for_match[username]
            del logged_users[client_address]
            print(f"[*] User {username} logged off.")
        if(log_event_level >= 4):
            print(f"[*] Connection closed from: {client_address[0]}:{client_address[1]}")

def handle_response(data, client_address, client_socket):
    global log_event_level
    message = data.get('message')
    command = data.get('command')
    token = data.get('token')
    response = {}

    
    if(command == "ping"):
        response = {"status": 200, "message": "pong", "command": "pong"}
    
    if(command == "request_images"):
        #verify Token for safety
        user_id, status = database.validate_token(token)
        if(status.get('status') != 200):
            return {"status": 401, "message": "Invalid Token", "command": "error"}
        
        if(log_event_level >= 5):
            print(f"[*] Files Requested from: {client_address[0]}:{client_address[1]}")
        
        for file in files:
            image_path, checksum = file
            response_json = json.dumps({"status": 200, "message": "images", "command": "request_images", "image": image_path, "checksum": checksum})
            client_socket.send(response_json.encode())
            #confirm the image was sent
            confirm = client_socket.recv(2048).decode()
            confirm = json.loads(confirm)
            if(confirm.get('command') == "image_received"):
                continue
        response = {"status": 200, "message": "images", "command": "request_images_end"}
        print(f"[*] File List sent to: {client_address[0]}:{client_address[1]}")
        
    elif(command == "download_images"):
        user_id, status = database.validate_token(token)
        if(status.get('status') != 200):
            return {"status": 401, "message": "Invalid Token", "command": "error"}
        
                
        if(log_event_level >= 5):
            print(f"[*] Sending image {data.get('image_path')} to: {client_address[0]}:{client_address[1]}")   
            
        streaming_assets_folder = getcwd() + "/StreamingAssets/"
        
        if(os.name == 'nt'):
            streaming_assets_folder = streaming_assets_folder.replace("/", "\\")
            
        image_path = streaming_assets_folder + data.get('image_path')    
        response = {"status": 200, "message": "images", "command": "file_download", "imageb64": image_to_b64(image_path)}
        
    elif(command == "logoff"):
        if(log_event_level >= 4):
            print(f"[*] Logoff: {client_address[0]}:{client_address[1]}")
        response = {"status": 200, "message": "Goodbye!", "command": "logoff"}
        
    elif(command == "chat"):
        if(log_event_level >= 5):
            print(f"[*] Chat message received: {message}")
        response = {"status": 200, "message": message, "command": "chat"}
        
    elif(command == "register"):
        if(log_event_level >= 2):
            print(f"[*] Registration request received, User: {data.get('username')}")
        response = register(data.get('username'), data.get('password'), client_address)
        
    elif(command == "login"):
        if(log_event_level >= 1):
            print(f"[*] Receiving login from user: {data.get('username')}")
        response = login(data.get('username'), data.get('password'), client_address)
        if(response['status'] == 200):
            print(f"[*] User {data.get('username')} logged in.")
        
    elif(command == "check_cards"):
        user_id = database.get_user_id(logged_users.get(client_address))[0]
        cards_from_user_cards = database.get_user_cards(user_id)
        card_list = []
        for card_v in cards_from_user_cards:
            #Get the card Name
            card_id = card_v[2]
            
            card = database.get_card_by_id(card_id)
            card_amount = database.get_card_amount(token, card_id)
            card_name = card[1]
            
            card_list.append((card_name, card_amount))
            
        response = {"status": 200, "message": "cards found:", "command": "check_cards", "cards": card_list}
    
    elif(command == "check_card"):
        response = database.get_card_info(data.get('card_name'))
        
    elif(command == "check_decks"):
        response = check_decks(logged_users.get(client_address))
        
    elif(command == "activate_deck"):
        user_id = database.get_user_id(logged_users.get(client_address))[0]
        deck_id = database.get_deck_id_by_name(data.get('deck_name'), user_id)
        if(deck_id == None):
            response = {"status": 500, "message": "Deck not found", "command": "error"}
        else:
            deck_id = deck_id[0]
        response = database.activate_deck(token, deck_id)
    
    elif(command == "create_deck"):
        user_id = database.get_user_id(logged_users.get(client_address))[0]
        deck_name = data.get('deck_name')
        response = database.add_deck(user_id, deck_name)
    
    elif(command == "add_card_to_deck"):
        user_id = database.get_user_id(logged_users.get(client_address))[0]
        deck_id = database.get_deck_id_by_name(data.get('deck_name'), user_id)
        if(deck_id == None):
            response = {"status": 500, "message": "Deck not found", "command": "error"}
        else:
            deck_id = deck_id[0]
        card_id = database.get_card_id(data.get('card_name'))
        if(card_id == None):
            response = {"status": 500, "message": "Card not found", "command": "error"}
        else:
            card_id = card_id[0]
        response = database.add_card_to_deck(deck_id, card_id)
    
    elif(command == "remove_card_from_deck"):
        user_id = database.get_user_id(logged_users.get(client_address))[0]
        deck_id = database.get_deck_id_by_name(data.get('deck_name'), user_id)
        if(deck_id == None):
            response = {"status": 500, "message": "Deck not found", "command": "error"}
        else:
            deck_id = deck_id[0]
        card_id = database.get_card_id(data.get('card_name'))
        if(card_id == None):
            response = {"status": 500, "message": "Card not found", "command": "error"}
        else:
            card_id = card_id[0]
        response = database.remove_card_from_deck(deck_id, card_id)
    
    elif(command == "delete_deck"):
        user_id = database.get_user_id(logged_users.get(client_address))[0]
        deck_id = database.get_deck_id_by_name(data.get('deck_name'), user_id)
        if(deck_id == None):
            response = {"status": 500, "message": "Deck not found", "command": "error"}
        else: 
            response = database.delete_deck(token, deck_id[0])
    
    elif(command == "check_deck"):
        user_id = database.get_user_id(logged_users.get(client_address))[0]
        deck_id = database.get_deck_id_by_name(data.get('deck_name'), user_id)
        if(deck_id != None):
            response = database.get_deck_info(token,deck_id[0])
        else:
            response = {"status": 500, "message": "Deck not found", "command": "error"}
        
    elif(command == "match_search"):
        username = logged_users.get(client_address)
        if(username == None):
            return {"status": 401, "message": "User not logged in", "command": "none"}
        if(log_event_level >= 3):
            print(f"[*] Match request received from: {username}")
        response = match.waiting_for_match(username, client_socket)
        
    else:
        response = {"status": 401, "message": "Invalid Command", "command": "none"}

    return response

def check_online_user(username):
    for connection, user in logged_users.items():
        if user == username:
            return True
    return False

def register(username, password, client_address):
    if(database.get_user_id(username)):
            return {"status": 500, "message": "User already exists", "command": "error"}
    else:
        if(len(password) < 6):
            return {"status": 500, "message": "Password too short", "command": "error"}
        cards_9 = database.get_9_random_cards()
        result = database.add_user(username, password)
        user_id = database.get_user_id(username)[0]
        # Add the cards to the new user
        for card in cards_9:
            database.add_card_to_user(user_id, card[0])
        
        # Add a default deck
        database.add_deck(user_id, "Default", 1)
        
        #grab deck id
        deck_id = database.get_deck_id_by_name("Default", user_id)
        print(deck_id)
        
        #add the cards to the deck
        for card in cards_9:
            database.add_card_to_deck(deck_id[0], card[0])
        
        database.make_deck_active(user_id, deck_id)
        
        return result

def login(username, password, client_address):
    if(check_online_user(username)):
        return {"status": 500, "message": "User already logged in", "command": "error"}
    response = database.login_user(username, password)
    if(response['status'] == 200):
        logged_users[client_address] = username
    
    #if there is no deck active, make the first deck active
    user_id = database.get_user_id(username)[0]
    if(database.get_active_deck(user_id) == None):
        deck_id = database.get_deck_id_by_name("Default", user_id)[0]
        database.make_deck_active(user_id, deck_id)
    
    return response

def make_deck(username, deck_name):
    user_id = database.get_user_id(username)
    if(user_id == None):
        return {"status": 500, "message": "User not found", "command": "error"}
    return database.add_deck(user_id, deck_name)
    
def check_decks(username):
    user_id = database.get_user_id(username)[0]
    if(user_id == None):
        return {"status": 500, "message": "User not found", "command": "error"}
    
    decks = database.get_user_decks(user_id)
    if(decks == None):
        return {"status": 500, "message": "No decks found", "command": "error"}
    
    return {"status": 200, "message": "decks found:", "command": "check_decks", "decks": decks}


def add_card_to_deck(username, deck_name, card_name):
    user_id = database.get_user_id(username)
    if(user_id == None):
        return {"status": 500, "message": "User not found", "command": "error"}
    
    deck_id = database.get_deck_id_by_name(user_id, deck_name)
    if(deck_id == None):
        return {"status": 500, "message": "Deck not found", "command": "error"}
    
    card_id = database.get_card_id(card_name)
    if(card_id == None):
        return {"status": 500, "message": "Card not found", "command": "error"}
    
    #check if deck has less than 9 cards
    if(database.get_deck_size(deck_id) >= 9):
        return {"status": 500, "message": "Deck is full", "command": "error"}
    
    return database.add_card_to_deck(deck_id, card_id)

def remove_card_from_deck(username, deck_name, card_name):
    user_id = database.get_user_id(username)
    if(user_id == None):
        return {"status": 500, "message": "User not found", "command": "error"}
    
    deck_id = database.get_deck_id_by_name(user_id, deck_name)
    if(deck_id == None):
        return {"status": 500, "message": "Deck not found", "command": "error"}
    
    card_id = database.get_card_id(card_name)
    if(card_id == None):
        return {"status": 500, "message": "Card not found", "command": "error"}
    
    return database.remove_card_from_deck(deck_id, card_id)

# Server-side commands
def add_cards():
    tamanho_dict = {1: "Minusculo", 2: "Pequeno", 3: "Medio", 4: "Grande", 5: "Enorme"}
    idade_dict = {1: "Jovem", 2: "Adolescente", 3: "Adulto", 4: "Anciao"}
    Tipo_dict = {1: "Terrestre", 2: "Voador", 3: "Aquatico"}
    
    print("[*] Adicionando carta ao banco de dados.")
    card_name = input(">> Nome da Carta: ")
    if(database.get_card_by_name(card_name)):
        print("Error: Card Already Exists")
        return
    card_group = input(">> Grupo da Carta: ")
    forca = int(input(">> Força [0-10]: "))
    fofura = int(input(">> Fofura [0-10]: "))
    velocidade = int(input(">> Velocidade [0-10]: "))
    tamanho = int(input(">> Tamanho[1-5] [Minusculo, Pequeno, Medio, Grande, Enorme]: "))
    idade = int(input(">> Idade[1-4] [Jovem, Adolescente, Adulto, Anciao]: "))
    tipo = int(input(">> Tipo[1-3] [Terrestre, Voador, Aquatico]: "))
    card_image = input(">> Nome da carta [arquivo]: ")
    path = "/StreamingAssets/" + card_image + ".png"
    print("")
    #verify cards attributes as valid
    if(forca < 0 or forca > 10):
        print("Error: Força")
        return
    if(fofura < 0 or fofura > 10):
        print("Error: Fofura")
        return
    if(velocidade < 0 or velocidade > 10):
        print("Error: Velocidade")
        return
    
    tamanho = tamanho_dict[tamanho]
    idade = idade_dict[idade]
    tipo = Tipo_dict[tipo]
            
    
    #Confirm card
    print("Nome: ", card_name)
    print("Grupo: ", card_group)
    print("Força: ", forca)
    print("Fofura: ", fofura)
    print("Velocidade: ", velocidade)
    print("Tamanho: ", tamanho)
    print("Idade: ", idade)
    print("Tipo: ", tipo)
    print("Imagem: ", path)
    print("")
    print("Add card? [y/n]")
    confirm = input()
    if(confirm == "n"):
        print("Card not added.")
        return
    
    database.add_card(card_name, card_group, forca, fofura, velocidade, tamanho, idade, tipo, path)

def add_test_cards():
    tamanho_dict = {1: "Minusculo", 2: "Pequeno", 3: "Medio", 4: "Grande", 5: "Enorme"}
    idade_dict = {1: "Jovem", 2: "Adolescente", 3: "Adulto", 4: "Anciao"}
    Tipo_dict = {1: "Terrestre", 2: "Voador", 3: "Aquatico"}      
    
    while(True):
        card_name = "Test Card {0}".format(random.randint(1, 100))        
        forca = random.randint(1, 10)
        fofura = random.randint(1, 10)
        velocidade = random.randint(1, 10)
        tamanho = random.randint(1, 5)
        idade = random.randint(1, 4)
        tipo = random.randint(1, 3)
        card_group = "Test Group"
        card_image = "Placeholder"
        path = "/StreamingAssets/" + card_image + ".png"
        if(database.get_card_by_name(card_name)):
            print(f"[*] Card Already Exists {card_name}")
            continue
        else:
            #get tamanho,idade and tipo as STRING
            tamanho = tamanho_dict[tamanho]
            idade = idade_dict[idade]
            tipo = Tipo_dict[tipo]
            
            print(tamanho)
            
            result = database.add_card(card_name, card_group, forca, fofura, velocidade, tamanho, idade, tipo, path)
            if(result['status'] == 200):
                print(f"[*] Card Added: {card_name}")
                print(f"[*] Força: {forca}")
                print(f"[*] Fofura: {fofura}")
                print(f"[*] Velocidade: {velocidade}")
                print(f"[*] Tamanho: {tamanho_dict[tamanho]}")
                print(f"[*] Idade: {idade_dict[idade]}")
                print(f"[*] Tipo: {Tipo_dict[tipo]}")
                print(f"[*] Grupo: {card_group}")
                print(f"[*] Imagem: {path}\n")
            break
        
def delete_card():
    print("[*] Deleting card from database.")
    card_name = input(">> Card Name: ")
    card = database.get_card_by_name(card_name)
    if(card):
        print(f"Card: {card}")
        print("Delete card? [y/n]")
        confirm = input()
        if(confirm == "y"):
            print(database.delete_card(card_name))
            return
        print("Card not deleted.")
        return
    else:
        print("Card not found.")

#StreamingAsset Functions

def image_to_b64(image_path):
    with open(image_path, "rb") as image_file:
        image_b64 = base64.b64encode(image_file.read()).decode('utf-8')
    return image_b64

def calculate_checksum(file_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def list_files(directory):  
    for item in os.listdir(directory):
        file_path = os.path.join(directory, item)
        if os.path.isfile(file_path):
            checksum = calculate_checksum(file_path)
            files.append((item, checksum))

if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description="Start the server with specified parameters.")
    parser.add_argument("-H", "--host", default="localhost", help="The host to bind the server to. Default is connection to LocalHost")
    parser.add_argument("-p", "--port", type=int, default=25555, help="The port to bind the server to. Default is 25555.")
    parser.add_argument("-l", "--log", type=int, default=4, help="The log event level. Default is 4 (Player Logins + Register + Matches + Connections). Maximum is 5.")
    
    args = parser.parse_args()
    
    host = args.host
    port = args.port
    log_event_level = args.log
    
    start_server(host, port)
