import base64
import select
import hashlib
import string
import threading
import json
import socket
import sys
import os
from time import sleep

stop_event = threading.Event()
token = ""
username = ""
login_into_server = False
searching_for_match = False
on_match = False
on_turn = False
downloading_file = False


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
        print("Commands: ")
        print("select_attribute <attribute>: Select an attribute to play")
        print("select_card <card>: Select a card to play")
        print("forfeit: Forfeit the match")
        print("check_card <card_name>: Check a specific card")
        send_status = False
        json_message = {"token": token, "message": "", "command": "chat"}
        
    return send_status, json_message
    
def common_commands(message, token):
    full_message = message.split(' ', 1)
    command = full_message[0]
    json_message = {}
    send_status = True
    
    if(command == "exit"):
        json_message = {"token": token, "message": "", "command": "logoff"}
    elif(command == "register"):
        send_status, json_message = register(message, token)
    elif(command == "login"):
        send_status, json_message = login(message, token)
    elif(command == "match_search"):
        send_status, json_message = match_search(token)           
    elif(command == "check_cards"):
        json_message = {"token": token, "message": "", "command": "check_cards"}
    elif(command == "check_card"):
        card_name = full_message[1]
        json_message = {"token": token, "message": "", "command": "check_card", "card_name": card_name}
    elif(command == "activate_deck"):
        deck_name = full_message[1]
        json_message = {"token": token, "message": "", "command": "activate_deck", "deck_name": deck_name}
    elif(command == "check_decks"):
        send_status, json_message = check_decks(token)
    elif(command == "add_card_to_deck"):
        send_status, json_message = add_card_to_deck(message, token)
    elif(command == "remove_card_from_deck"):
        send_status, json_message = remove_card_from_deck(message, token)
    elif(command == "create_deck"):
        send_status, json_message = create_deck(message, token)
    elif(command == "delete_deck"):
        send_status, json_message = delete_deck(message,token)
    elif(command == "check_deck"):
        send_status, json_message = check_deck(message, token)
    elif(command == "msg"):
        if not token:
            return False, {"token": token, "message": "Not logged in", "command": "error"}
        two_parts = message.split(' ', 2)
        if(len(two_parts) != 3):
            return False, {"token": token, "message": "Invalid input", "command": "error"}
        receiver = two_parts[1]
        message = two_parts[2]
        json_message = {"token": token, "message": message, "command": "msg", "receiver": receiver}
    elif(command == "help"):
        help()
        send_status = False
        json_message = {"token": token, "message": "", "command": "chat"}
    else:
        json_message = {"token": token, "message": message, "command": "chat"}
    
    return send_status, json_message

def package_message(message, token="none"):
    global searching_for_match
    global on_match
    json_message = {}
    send_status = True

    try:
        if(on_match):
            send_status, json_message = match_commands(message, token)
        else:
            send_status, json_message = common_commands(message, token)
    except Exception as e:
                json_message = {"token": token, "message": f"Error: {str(e)}", "command": "error"}
                send_status = False

    return send_status, json_message

def help():
    print("Commands:")
    print("register <username> <password>: Register a new user")
    print("login <username> <password>: Login with a user")
    print("match_search: Search for a match")
    print("check_cards: Check all cards")
    print("check_card <card_name>: Check a specific card")
    print("create_deck <deck_name>: Create a new deck")
    print("delete_deck <deck_name>: Delete a deck")
    print("activate_deck <deck_name>: Activate a deck")
    print("add_card_to_deck <deck_name> <card_name>: Add a card to a deck")
    print("remove_card_from_deck <deck_name> <card_name>: Remove a card from a deck")
    print("check_decks: Check all decks")
    print("check_deck <deck_name>: Check a specific deck")
    print("exit: Close the client")

def receive_message(client_socket):
    global stop_event
    global username
    global token
    global on_match
    global login_into_server
    
    response_json = {}
    data = b""
    while not stop_event.is_set():
        try:
            response = client_socket.recv(4096)
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
                continue
            
            message = response_json.get('message')
            command = response_json.get('command')
            
            # print(f"[*] Received: {response_json}")
            if(command == "ping"):
                continue
            elif(command == "login"):
                token = response_json.get('token')
                username = response_json.get('username')
                login_operation(client_socket)
            
            elif(command == "logoff"):
                print(f"[*] Turning off")
                sleep(0.5)
                stop_event.set()
                return
            
            elif(command == "serverside_logoff"):
                reason = response_json.get('message')
                print(f"[*] You have been disconnected from the server.")
                print(f"[*] Reason: {reason}")
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
                print(" > Card: ", card_name)
                print(" > Forca: ", forca)
                print(" > Fofura: ", fofura)
                print(" > Velocidade: ", velocidade)
                print(" > Tamanho: ", tamanho)
                print(" > Idade: ", idade)
                print(" > Tipo: ", tipo)
                print(" > Imagem: ", imagem)
            
            elif(command == "check_cards"):
                cards = response_json.get('cards')
                for card in cards:
                    print(f"[*] Card: {card[0]} Amount: {card[1]}")
            
            elif(command == "create_deck"):
                deck_name = response_json.get('deck_name')
                print(f"[*] Deck {deck_name} created")
            
            elif(command == "delete_deck"):
                deck_name = response_json.get('deck_name')
                print(f"[*] Deck {deck_name} deleted")
            
            elif(command == "check_decks"):
                decks = response_json.get('decks')
                for deck in decks:
                    # grab out the ID, Name, User ID, Active and default
                    deck_id, deck_name, user_id, active, default = deck
                    if(active == 1):
                        active = "Yes"
                    else:
                        active = "No"
                    if(default == 1):
                        default = "Yes"
                    else:
                        default = "No"
                    print(f"[*] Deck Name: {deck_name}, Active: {active}, Default: {default}")

            elif(command == "check_deck"):
                deck = response_json.get('deck_name')
                cards = response_json.get('cards')
                active = response_json.get('active')
                
                print(f"[*] Deck: {deck}, Active: {active}")
                for card in cards:
                    print(f"[*] Card: {card}")                
            
            elif(command == "activate_deck"):
                deck_name = response_json.get('deck_name')
                print(f"[*] Deck {deck_name} activated")
                
            elif(command == "add_card_to_deck"):
                card_name = response_json.get('card_name')
                deck_name = response_json.get('deck_name')
                print(f"[*] Card {card_name} added to deck {deck_name}")
                
            elif(command == "remove_card_from_deck"):
                card_name = response_json.get('card_name')
                deck_name = response_json.get('deck_name')
                print(f"[*] Card {card_name} removed from deck {deck_name}")
                
            #Match Commands    
            elif(command == "match_start"):
                player_1 = response_json.get('player_1')
                player_2 = response_json.get('player_2')
                player_3 = response_json.get('player_3')
                print("\n")
                print(f"[*] Match started between {player_1}, {player_2} and {player_3}")
                on_match = True
            elif(command == "match_end"):
                on_match = False
                print(f"[*] Match ended.")
                print(f"[*] {message}")
            elif(command == "error"):
                print(f"[*] Error: {message}")
            elif(command == "select_attribute"):
                print(f"[*] Select a attribute")
                print(f"[*] Attributes: Forca, Fofura, Velocidade, Tamanho, Idade, Tipo")
            elif(command == "select_card"):
                attribute_in_play = response_json.get('attribute')
                hand = response_json.get('hand')
                print(f"[*] Select a card")
                print(f"[*] Attribute in play: {attribute_in_play}")
                x = 0
                for card, card_value in hand:
                    print(f"[*] Card: {card[1]} Value: {card_value}")
                    x += 1
            elif(command == "your_turn"):
                print(f"[*] Your turn")
            elif(command == "opponent_turn"):
                print(f"[*] Opponent turn")
            elif(command == "turn_end"):
                winner = response_json.get('winner')
                print(f"[*] Turn ended")
                print(f"[*] Winner: {winner}")
                print(f"[*] {message}")
                
            elif(command == "reward"):
                print(f"[*] Reward: {response_json.get('card')}")      
            elif(command == "card_hand"):
                hand = response_json.get('hand')  
                cards = response_json.get('cards')
                print(f"[*] Remaining in deck: {cards}")
                for card in hand:
                    print(f"[*] Card: {card[1]}")    
            elif(command == "msg"):                    
                sender = response_json.get('sender')
                message = response_json.get('message')
                print(f"\n[*] Message from {sender}: {message}")
            else:
                print(f"[*] Message: {message}")    
        except KeyboardInterrupt:
            print("\n[*] User interruption.")
            stop_event.set()
            exit(0)
        except Exception as e:
            print(f"[*] Receive Exception: {str(e)}")
            sleep(4)
            stop_event.set()
            return

def client_handler(client_socket):
    global stop_event
    global token
    global username
    global login_into_server
    global on_match
    
    try:        
        while not stop_event.is_set():
            if not login_into_server:
                message = input("Enter a message: ")
            else:
                if(on_match):
                    match_handler(client_socket)
                sleep(1)
                continue
            if(message and not stop_event.is_set()):
                send_status, packed_message = package_message(message, token)
                if not send_status:
                    print(f"[*] {packed_message.get('message')}")
                    continue
                package = json.dumps(packed_message)
                client_socket.send(package.encode())
                sleep(0.25)

    except KeyboardInterrupt:
        print("\n[*] User interruption.")
        stop_event.set()
        exit(0)
    except Exception as e:
        print(f"[*] Sender Exception: {str(e)}")
        return            

def match_handler(client_socket):
    global on_match
    global on_turn
    while not stop_event.is_set() and on_match:
        pass 
    
#Start Client
def start_client(host, port):
    global stop_event
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print(f"[*] Connection refused to {host}:{port}")
        sleep(2)
        return
    print(f"[*] Connected to {host}:{port}")   

    

    client_handler_tread = threading.Thread(target=client_handler, args=(client_socket,))
    client_handler_tread.start()
    receive_message_thread = threading.Thread(target=receive_message, args=(client_socket,))
    receive_message_thread.start()
   

    try:
        while not stop_event.is_set():
            sleep(1)
    except KeyboardInterrupt:
        print("\n[*] User interruption, exiting.")
        stop_event.set()
    
    if(client_handler_tread.is_alive()):
        client_handler_tread.join()
    
    if(receive_message_thread.is_alive()):
        receive_message_thread.join()

    close_connection(client_socket)
        
# Aux Functions
def register(message, token):
    
    if(token):
        return False, {"token": token, "message": "Already logged in", "command": "error"}

    parts = message.split(' ', 2)

    if(len(parts) != 3):
        return False, {"token": token, "message": "Invalid input", "command": "error"}

    username = parts[1]
    password = parts[2]

    if(len(password) < 6):
        return False, {"token": token, "message": "Password too short", "command": "error"}
    return True, {"token": token, "message": "requesting registration", "command": "register", "username": username, "password": password}

def login(message, token):
    if(token):
        return False, {"token": token, "message": "Already logged in", "command": "error"}

    parts = message.split(' ', 2)
    if(len(parts) != 3):
        return False, {"token": token, "message": "Invalid input", "command": "error"}
    
    username = parts[1]
    password = parts[2]

    if(len(password) < 6):
        return False, {"token": token, "message": "Password too short", "command": "error"}
    return True, {"token": token, "message": "requesting login", "command": "login", "username": username, "password": password}

def match_search(token):
    if(not token):
        return False, {"token": token, "message": "Not logged in", "command": "error"}
    global searching_for_match
    if(searching_for_match):
        return False, {"token": token, "message": "Already searching for match", "command": "error"}
    searching_for_match = True
    return True, {"token": token, "message": "Match Search", "command": "match_search"} 

def create_deck(message, token):
    if(not token):
        return False, {"token": token, "message": "Not logged in", "command": "error"}
    
    parts = message.split(' ', 2)
    if(len(parts) != 2):
        return False, {"token": token, "message": "Invalid input", "command": "error"}
    
    deck_name = parts[1]
    return True, {"token": token, "message": "Creating deck", "command": "create_deck", "deck_name": deck_name}

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
    print(parts)
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

def check_decks(token):
    if(not token):
        return False, {"token": token, "message": "Not logged in", "command": "error"}
    return True, {"token": token, "message": "Checking decks", "command": "check_decks"}
    
def check_deck(message, token):
    if(not token):
        return False, {"token": token, "message": "Not logged in", "command": "error"}
    
    parts = message.split(' ', 2)
    if(len(parts) != 2):
        return False, {"token": token, "message": "Invalid input", "command": "error"}
    
    deck_name = parts[1]
    return True, {"token": token, "message": "Checking deck", "command": "check_deck", "deck_name": deck_name}

#Login Operation
def login_operation(client_socket):
    global login_into_server 
    global token
    server_files = []
    x = 0
    
    login_into_server= True
    
    print(f"[*] Logging in...")
    print(f"[*] Loading... Please wait ")
    client_socket.send(json.dumps({"token": token, "message": "", "command": "request_images"}).encode())
    while(True):
        response = client_socket.recv(4096)
        if not response:
            continue
        response = response.decode()
        response_json = json.loads(response)
        if(response_json == None):
            print(f"[*] Empty Packet")
            continue
        command = response_json.get('command')
        if(command == "request_images"):
            server_files.append((response_json.get('image'), response_json.get('checksum')))
            client_socket.send(json.dumps({"token": token, "message": "", "command": "image_received"}).encode())
        elif(command == "request_images_end"):
            print(f"[*] There exists {len(server_files)} files.")
            amount, missing_indexes = verify_files(server_files)
            if(amount == 0):
                print("[*] All files are up to date.")
                break
            else:
                print(f"[*] Missing {amount} files.")
                sleep(2)
                download_files(client_socket, missing_indexes, amount, server_files, token)
                break
        else:
            print(f"[*] Unknown command: {command} {response_json.get('message')}")
            
    login_into_server = False
                      
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
                print(f"[*] File {path} downloaded.")
                x += 1
        except Exception as e:
            print(f"[*] Download Exception: {str(e)}")
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
            print(f"[*] Missing file: {file_name}")
        else:
            server_file_checksum = file[1]
            #check the checksum
            if(server_file_checksum not in files_checksum):
                missing_indexes.append(server_files.index(file))
                missing_files += 1
                print(f"[*] File {file_name} is outdated or corrupted.")

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
    host = "localhost"
    port = 25555
    if(len(sys.argv) == 3):
        host = sys.argv[1]
        port = int(sys.argv[2])
    #start = offline_commands()
    start = True
    if(start):
        directory_maker()
        start_client(host, port)

