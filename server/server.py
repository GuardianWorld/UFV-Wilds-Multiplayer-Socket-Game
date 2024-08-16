from os import getcwd
import argparse
import random
import sys
import json
import threading
import time
import datetime
import signal
import hashlib
import base64
import os
import Pyro5.api
import queue


import database
from config import stop_event, logged_users, match_rooms, log_event_level, delay_for_lag
import match

files = []

#Signal Handling
def signal_handler(sig, frame):
    print(f"[*] Signal received: {sig}. Shutting down...")
    shutdown_server(5)

signal.signal(signal.SIGTERM, signal_handler)    

@Pyro5.api.expose
class UFVWildsServer:
    def __init__(self):
        self.client_queues = {}
        self.clients = []
        self.logged_users = {}
        self.heartbeats = {}
        self.searching_for_match = {}

    #Connection Management

    def set_connection(self):
        #make unique ID
        client_id = hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()
        self.clients.append(client_id)
        self.client_queues[client_id] = queue.Queue()
        return client_id
    
    def heartbeats_check(self):
        try:
            current_time = time.time()
            for client_id, _time in self.heartbeats.items():
                if(current_time - _time > 60):
                    print(f"[*] Client {client_id} timed out.")
                    self.logoff(client_id)
        except Exception as e:
            pass
            
                
    def update_heartbeat(self, client_id):
        try:
            current_time = time.time()
            self.heartbeats[client_id] = current_time
        except Exception as e:
            print(f"Error: {e}")
    
    #Account Management
    
    def register(self, username, password):
        if(log_event_level >= 2):
            print(f"[*] Registration request received, User: {username}")
            
        if(database.get_user_id(username)):
            return 500, "User already exists."
        
        if(len(password) < 6):
            return 500, "Password too short."
        
        result = database.add_user(username, password)
        if(result['status'] == 500):
            return 500, "Error: User not added."
        
        user_id = database.get_user_id(username)[0]
        cards_9 = database.get_9_random_cards()
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
        
        return 200, f"User {username} registered sucessfully."
        
        
    def login(self, username, password, client_id):
        if(log_event_level >= 1):
            print(f"[*] Login request received, User: {username}")
        Token = ""
        
        if(check_online_user(username)):
            return 500, ""
        response = database.login_user(username, password)
        status = response['status']
        if(response['status'] == 200):
            if(log_event_level >= 1):
                print(f"[*] User {username} logged in.")
            Token = response.get('token')
            self.logged_users[client_id] = Token
            
            #Check if user has active decks.
            user_id = database.get_user_id(username)[0]
            if(database.get_active_deck(user_id) == None):
                deck_id = database.get_deck_id_by_name("Default", user_id)[0]
                database.make_deck_active(user_id, deck_id)
        
        return status, Token
    
    def logoff(self, client_id):
        if client_id in self.heartbeats:
            del self.heartbeats[client_id]
        if client_id in self.client_queues:
            del self.client_queues[client_id]
        if client_id in self.clients:
            self.clients.remove(client_id)
        if client_id in self.logged_users:
            del self.logged_users[client_id]
        return "Goodbye!"
    
    #Download Management
    def request_images(self, client_id):
        if(log_event_level >= 5):
            print(f"[*] Image request received from {client_id}")
        response = {"status": 200, "message": "Images received", "command": "request_images", "images": files}
        return response
    
def heartbeat_thread(server):
    while not stop_event.is_set():
        server.heartbeats_check()
        time.sleep(5)

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
    
    print("[*] Server started.")
    #print(f"[*] Listening on {host}:{port}")
    print(f"[*] Log Level: {log_event_level}")  
    
    #Pyro Server
    daemon = Pyro5.api.Daemon(host=host, port=port)
    ns = Pyro5.api.locate_ns()
    
    ufv_wilds_server = UFVWildsServer()
    uri = daemon.register(ufv_wilds_server)
    ns.register("ufv_wilds.server", uri)
    
    terminal = threading.Thread(target=internal_server_terminal)
    terminal.start()
    
    #match_thread = threading.Thread(target=match.search_match)
    #match_thread.start()
    
    heartbeat = threading.Thread(target=heartbeat_thread, args=(ufv_wilds_server,))
    heartbeat.start()
    
    def loop_condition():
        global stop_event
        return not stop_event.is_set()
    
    # Pyro request loop
    daemon.requestLoop(loop_condition)
    
    terminal.join()
    #match_thread.join()
    heartbeat.join()
    
    shutdown_server(1)

#Shutdown Server
def shutdown_server(timeout=5):
    print(f"[*] Shutting down server in {timeout} seconds.")
    stop_event.set()
    time.sleep(timeout)
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
            #remove from connections
            client_socket.close()
            del active_connections[client_address]
            #delete from logged users
            del logged_users[client_address]
            print(f"[*] User {username} kicked.")
            #del from match search
            if(match.player_searching(username)):
                del searching_for_match[username]
            return
    

#endregion


def check_online_user(username):
    for connection, user in logged_users.items():
        if user == username:
            return True
    return False

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
    parser.add_argument("-dl", "--delay", type=float, default=0.1, help="The delay between socket messages. Default is 0.1 seconds.")
    
    args = parser.parse_args()
    
    host = args.host
    port = args.port
    log_event_level = args.log
    delay_for_lag = args.delay
    
    start_server(host, port)
