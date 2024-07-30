from os import getcwd
import random
import sys
import socket
import json
import threading
import time
import datetime
import signal


import database
from config import active_connections, stop_event, logged_users, searching_for_match, match_rooms, log_event_level
import match

#Signal Handling
def signal_handler(sig, frame):
    print(f"[*] Signal received: {sig}. Shutting down...")
    shutdown_server(5)

signal.signal(signal.SIGTERM, signal_handler)

#Start Server
def start_server(host, port):

    #Open DB
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

    print(f"[*] Listening on {host}:{port}")

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
    shutdown_server()
    server_socket.close()

#Shutdown Server
def shutdown_server(timeout=5):
    print(f"[*] Shutting down server in {timeout} seconds.")
    stop_event.set()
    time.sleep(timeout)
    for _, client_socket, _ in active_connections.items():
        client_socket.close()
    sys.exit(0)

# region Internal Server Terminal

def internal_server_terminal():
    global log_event_level
    log_event_level = 5
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
            elif command == "ban":
                terminal_user_ban()      
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
                print(" >> ban - Ban/Unbans a user.")
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
        print(" >> exit - Exits configuration.")
        command = input("[config] >> ")
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
    
def search_card():
    print("[*] Search for cards by name.")
    card_name = input("[search card] >> ")
    card = database.get_card(card_name)
    if(card):
        print(f"Card: {card}")
    else:
        print("Card not found.")    
        
def all_cards():
    print("[*] All cards.")
    cards = database.get_all_cards()
    for card in cards:
        print(f" >> {card}")

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

#endregion

#Server-Client Side

def handle_client(client_socket, client_address):     
    global log_event_level   
    if(log_event_level >= 4):
        print(f"[*] Accepted connection from: {client_address[0]}:{client_address[1]}")
    active_connections[client_address] = (client_socket, datetime.datetime.utcnow())
    if not client_socket:
        return
    
    client_socket.settimeout(5.0)
    
    try:
        while not stop_event.is_set():
            try:
                if(client_address in logged_users):
                    if(match.player_in_match(logged_users[client_address])):
                        print(f"[*] Player {logged_users[client_address]} is in match.")
                        #wait until match is over
                        while match.player_in_match(logged_users[client_address]):
                            time.sleep(1)
                        
                request = client_socket.recv(4096)
                if not request:
                    break
                data = json.loads(request.decode())
                response = json.dumps(handle_response(data, client_address, client_socket))
                client_socket.send(response.encode())
            except socket.timeout:
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
        
        # Add the cards to the new user
        for card in cards_9:
            database.add_card_to_user(card[0], result['id'])
        
        # Add a new deck with the cards.
        #database.add_deck(result['id'], cards_9)
        
        return result

def login(username, password, client_address):
    if(check_online_user(username)):
        return {"status": 500, "message": "User already logged in", "command": "error"}
    response = database.login_user(username, password)
    if(response['status'] == 200):
        logged_users[client_address] = username
    
    return response

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
    forca = input(">> Força [0-10]: ")
    fofura = input(">> Fofura [0-10]: ")
    velocidade = input(">> Velocidade [0-10]: ")
    tamanho = input(">> Tamanho[1-5]: ")
    idade = input(">> Idade[1-4]: ")
    tipo = input(">> Tipo[1-3] [Terrestre, Voador, Aquatico]: ")
    card_image = input(">> Nome da carta [arquivo]: ")
    path = "/StreamingAssets/" + card_image + ".png"
    
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
    if(tamanho < 1 or tamanho > 5):
        print("Error: Tamanho")
        return
    if(idade < 1 or idade > 4):
        print("Error: Idade")
        return
    if(tipo < 1 or tipo > 3):
        print("Error: Tipo")
        return
    
    #Confirm card
    print("Nome: ", card_name)
    print("Grupo: ", card_group)
    print("Força: ", forca)
    print("Fofura: ", fofura)
    print("Velocidade: ", velocidade)
    print("Tamanho: ", tamanho_dict[tamanho])
    print("Idade: ", idade_dict[idade])
    print("Tipo: ", Tipo_dict[tipo])
    print("Imagem: ", path)
    
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
            result = database.add_card(card_name, card_group, forca, fofura, velocidade, tamanho_dict[tamanho], idade_dict[idade], Tipo_dict[tipo], path)
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
        
    

if __name__ == "__main__":
    host = ""
    port = 25555
    if len(sys.argv) == 2:
        port = int(sys.argv[1]) 
    
    start_server(host, port)
