import base64
import select
import string
import threading
import json
import socket
import sys
from time import sleep

stop_event = threading.Event()
token = ""
username = ""
searching_for_match = False
on_match = False

def close_connection(client_socket):
    print("[*] Disconnected from server.")
    client_socket.close()
    
def package_message(message, token="none"):
    global searching_for_match
    full_message = message.split(' ', 1)
    command = full_message[0]
    json_message = {}
    send_status = True

    try:
        if(command == "exit"):
            json_message = {"token": token, "message": "", "command": "logoff"}
        elif(command == "register"):
            send_status, json_message = register(message, token)
        elif(command == "login"):
            send_status, json_message = login(message, token)
        elif(command == "match_search"):
            send_status, json_message = match_search(token)           
        elif(command == "activate_deck"):
            deck_name = full_message[1]
            json_message = {"token": token, "message": "", "command": "activate_deck", "deck_name": deck_name}
        elif(command == "check_decks"):
            json_message = {"token": token, "message": "", "command": "check_decks"}         
        else:
            json_message = {"token": token, "message": message, "command": "chat"}
    except Exception as e:
                json_message = {"token": token, "message": f"Error: {str(e)}", "command": "error"}
                send_status = False

    return send_status, json_message

def receive_message(client_socket):
    global stop_event
    global username
    global token
    global on_match
    
    while not stop_event.is_set():
        try:
            response = client_socket.recv(4096).decode()
            response_json = json.loads(response)
            if(response_json == None):
                print(f"[*] Empty Packet")
                continue
            
            message = response_json.get('message')
            command = response_json.get('command')
            
            print(f"[*] Received: {response_json}")
            if(command == "ping"):
                continue
            elif(command == "login"):
                token = response_json.get('token')
                username = response_json.get('username')
                print(f"[*] Logged in as {username}")
            elif(command == "logoff"):
                print(f"[*] Turning off")
                sleep(0.2)
                stop_event.set()
                return
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
                print(f"[*] Decks: {decks}")
            elif(command == "activate_deck"):
                deck_name = response_json.get('deck_name')
                print(f"[*] Deck {deck_name} activated")
            elif(command == "match_start"):
                player_1 = response_json.get('player_1')
                player_2 = response_json.get('player_2')
                player_3 = response_json.get('player_3')
                print(f"[*] Match started between {player_1}, {player_2} and {player_3}")
                on_match = True
            elif(command == "match_end"):
                on_match = False
                print(f"[*] Match ended.")
            elif(command == "error"):
                print(f"[*] Error: {message}")
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
    try:
        debugger_auto(client_socket)
        
        while not stop_event.is_set():
            message = input("Enter a message: ")
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
        
def debugger_auto(client_socket):  
    message = ["login mixxs 123456", "login marcos 123456", "login alan 123456", "match_search"]

    for x in range (0, 4):
        msg = message[x]
        send_status, packed_message = package_message(msg, token)
        package = json.dumps(packed_message)
        client_socket.send(package.encode())
        sleep(0.25)
            
    
    
            
        
    

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
    #alive_thread.join()
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
    

#Send IMAGES
def image_to_b64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_image(host, port, token, image_path):
    try:
        # Convert the image to base64
        image_base64 = image_to_b64(image_path)

        # Create the JSON payload
        payload = {
            "token": token,
            "command": "add_card",
            "card_name": "SampleCard",
            "card_group": "Group1",
            "forca": 10,
            "fofura": 8,
            "velocidade": 7,
            "tamanho": 5,
            "idade": 3,
            "tipo": "Fire",
            "imagem": image_base64
        }

        # Convert the payload to a JSON string
        payload_json = json.dumps(payload)

        # Establish socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"[*] Connected to {host}:{port}")

        # Send the JSON payload
        client_socket.sendall(payload_json.encode('utf-8'))

        # Receive the response from the server
        response = client_socket.recv(4096)
        print(f"Received: {response.decode('utf-8')}")

        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")


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
        start_client(host, port)

