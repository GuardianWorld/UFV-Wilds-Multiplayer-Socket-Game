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
downloading_file = False
client_id = ""

@Pyro5.api.expose
class Client:
    def __init__(self):
        pass
    
    def match_search(self):
        print("[*] Searching for a match.")
    
    def match_start(self, player_1, player_2, player_3):
        global on_match
        print(f"[*] Match started between {player_1}, {player_2} and {player_3}")
        response_queue.put(["Match started", player_1, player_2, player_3])
        on_match = True
    def match_end(self):
        global on_match
        
        print("[*] Match ended.")
        response_queue.put("Match ended")
        on_match = False
    def select_attribute(self):
        print("[*] Select an attribute.")
        response_queue.put("Select attribute")
        while(True):
            request = message_queue.get()
            print(f"[*] Selected attribute: {request}")
            if(request == "Forca" or request == "Fofura" or request == "Velocidade" or request == "Tamanho" or request == "Idade" or request == "Tipo"):
                return request
        return "Invalid"
    def select_card(self, attribute):
        response_queue.put("Select card")
        response_queue.put(attribute)
        response = message_queue.get()
        print(f"[*] Selected card: {response}")
        return response
    def your_turn(self):
        response_queue.put("Your turn")
    def opponent_turn(self):
        response_queue.put("Opponent turn")
    def turn_end(self, winner):
        response_queue.put(["Turn ended", winner])
    def card_hand(self, cards, hand):
        response_queue.put([cards,hand])
    def reward(self, reward):
        response_queue.put(reward)
    def error(self, message):
        response_queue.put(["Error", message])
        
 
def common_commands(message, server):
    global username
    global token
    global on_match
    full_message = message.split(' ', 1)
    command = full_message[0]
    
    if(command == "register"):
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
        print(status, cards)
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
    
    elif(command == "exit"):
        response = server.logoff(client_id)
    elif(command == "match_search"):
        on_match = True

        
        try:
            status, response = server.match_search(token, client_id, client_uri)
            print(f"[*] Match Search: {status}")
            print(f"[*] Match Search Response: {response}")
        except Exception as e:
            print(f"[*] Match Search Exception: {str(e)}")
            on_match = False
            exit(0)
             

def package_message(message, server):
    global searching_for_match
        
    try:
        common_commands(message, server)
    except Exception as e:
        print(f"[*] Package Exception: {str(e)}")
        response_queue.put(["Package exception", str(e)])
    
    return

def heartbeats(address, host, port):
    ns = Pyro5.api.locate_ns(host=host, port=port)                           
    uri = ns.lookup(address)            
    server = Pyro5.api.Proxy(uri)                         
    while not stop_event.is_set():
        try:
            server.update_heartbeat(client_id)
            sleep(5)
        except Exception as e:
            print(f"[*] Heartbeat Exception: {str(e)}")
            return
    
#Start Client
def start_client(host, port):
    global stop_event
    global token     
    global client_uri
    global client_handler 
    global client_id
    
    print("[*] Starting Up... Please wait...")
    try:
        ns = Pyro5.api.locate_ns(host=host, port=port)                           
        uri = ns.lookup("ufv_wilds.server")             
        server = Pyro5.api.Proxy(uri)    
        
        client_id = server.set_connection()
        
        if(not client_id):
            stop_event.set()
            return

        print(f"[*] Connected to the server.")
        print(f"[*] Client ID: {client_id}", flush=True)
            
        client_handler = Client()
        client_daemon = Pyro5.api.Daemon()
        client_uri = client_daemon.register(client_handler)
        
        print(f"[*] Generated Client URI: {client_uri}")
        
        unique_name = f"Client-Match {client_id}"
        ns.register(unique_name, client_uri)
        registered_uri = ns.lookup(unique_name)
        print(f"[*] Registered URI: {registered_uri}")
    except:
        print("[*] Server not found.")
        stop_event.set()
        return
            
    file_checking(server, client_id)    
    
    
    heartbeats_thread = threading.Thread(target=heartbeats, args=("ufv_wilds.server",host, port))
    heartbeats_thread.start()
                  
    ui_thread = threading.Thread(target=startInterface, args=(message_queue, response_queue))
    ui_thread.start()
    
    def request_loop():
        def loop_condition():
            return not stop_event.is_set()
        client_daemon.requestLoop(loop_condition)
    
    loop_thread = threading.Thread(target=request_loop)
    loop_thread.start()
    
    try:
        while not stop_event.is_set():
            if(on_match):
                sleep(1)
                continue
            if not message_queue.empty():
                message = message_queue.get()
                print("enviado:", message)
                if(message == "exit"):
                    server.logoff(client_id)
                    stop_event.set()
                    break
                package_message(message, server)
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
    loop_thread.join()

        
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
