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
from config import active_connections, stop_event, logged_users, log_event_level

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
    while not stop_event.is_set():
        try:
            client_socket, client_address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address,))
            client_handler.start()
        except socket.timeout:
            continue
    
    terminal.join()
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

#Internal Server Side
def internal_server_terminal():
    print("[*] Server terminal started.")
    try:
        while not stop_event.is_set():
            command = input("")
            if command == "shutdown":
                print("[*] Shutdown command issued, stopping...")
                stop_event.set()
            if command == "status":
                number_of_sockets = len(active_connections)
                print("[*] Server is running.")
                print(f"[*] Number of sockets open: {number_of_sockets}")
                print(f"[*] Active connections: ")
                for connection, socket_time_pair in active_connections.items():
                    print(f" >> {connection[0]}:{connection[1]} - {socket_time_pair[1]}")
            if command == "users":
                number_of_users = len(logged_users)
                print("[*] Number of Users Online: ", number_of_users)
                for connection, user in logged_users.items():
                    print(f" >> {connection[0]}:{connection[1]} [{user}]")
            if command == "config":
                config()           
            if command == "help":
                print("[*] Available commands: ")
                print(" >> shutdown - Stops the server.")
                print(" >> status - Shows server status.")
                print(" >> users - Shows online users.")
                print(" >> config - Shows server configuration.")
                print(" >> help - Shows this message.")
    except KeyboardInterrupt:
        print("\n[*] Keyboard interruption.")
    except Exception as e:
        print(f"Error: {e}")

    print("[*] Server terminal stopped.")

def config():
    print("[*] Configuring server.")
    print("[*] Available commands: ")
    print(f" >> log level - Sets the log level. Current: {log_event_level}")
    print(" >> addcard - Adds a card to the database.")
    print(" >> addtestcards - Adds test cards to the database.")
    print(" >> exit - Exits configuration.")

    while(command != "exit"):
        command = input("config command: ")
        if(command == "log level"):
            print("    >> 0 - No logs.")
            print("    >> 1 - Player Logins")
            print("    >> 2 - Player Logins + Register")
            print("    >> 3 - Player Logins + Register + Matches")
            print("    >> 4 - Player Logins + Register + Matches + Connections")
            print("    >> 5 - Player Logins + Register + Matches + Connections + Debug")
            log_event_level = int(input("Log Level: "))
        elif(command == "addcard"):
            add_cards()
        elif(command == "addtestcards"):
            input = int(input("Quantas cartas deseja adicionar?"))
            for i in range(input):
                add_test_cards()
    
    
    

#Server-Client Side

def handle_client(client_socket, client_address):        
    if(log_event_level >= 4):
        print(f"[*] Accepted connection from: {client_address[0]}:{client_address[1]}")
    active_connections[client_address] = (client_socket, datetime.datetime.utcnow())
    if not client_socket:
        return
    
    client_socket.settimeout(5.0)
    
    try:
        while not stop_event.is_set():
            try:
                request = client_socket.recv(4096)
                #print(request)
                if not request:
                    break
                data = json.loads(request.decode())
                response = json.dumps(handle_response(data, client_address))
                client_socket.send(response.encode())
            except socket.timeout:
                continue
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        del active_connections[client_address]
        if client_address in logged_users:
            del logged_users[client_address]
        if(log_event_level >= 4):
            print(f"[*] Connection closed from: {client_address[0]}:{client_address[1]}")

def handle_response(data, client_address):

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
        
        return database.add_user(username, password)

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
        print("Força invalida")
        return
    if(fofura < 0 or fofura > 10):
        print("Fofura invalida")
        return
    if(velocidade < 0 or velocidade > 10):
        print("Velocidade invalida")
        return
    if(tamanho < 1 or tamanho > 5):
        print("Tamanho invalido")
        return
    if(idade < 1 or idade > 4):
        print("Idade invalida")
        return
    if(tipo < 1 or tipo > 3):
        print("Tipo invalido")
        return
    if(database.get_card(card_name)):
        print("Carta ja existe.")
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
    
    print("Adicionar carta? [y/n]")
    confirm = input()
    if(confirm != "n"):
        print("Carta nao adicionada.")
        return
    
    database.add_card(card_name, card_group, forca, fofura, velocidade, tamanho, idade, tipo, path)


def add_test_cards():
    tamanho_dict = {1: "Minusculo", 2: "Pequeno", 3: "Medio", 4: "Grande", 5: "Enorme"}
    idade_dict = {1: "Jovem", 2: "Adolescente", 3: "Adulto", 4: "Anciao"}
    Tipo_dict = {1: "Terrestre", 2: "Voador", 3: "Aquatico"}      
    
    while(True):
        card_name = "Test Card {0}".format(random.randint(1, 1000))        
        forca = random.randint(1, 10)
        fofura = random.randint(1, 10)
        velocidade = random.randint(1, 10)
        tamanho = random.randint(1, 5)
        idade = random.randint(1, 4)
        tipo = random.randint(1, 3)
        card_group = "Test Group"
        card_image = "Placeholder"
        path = "/StreamingAssets/" + card_image + ".png"
        if(database.get_card(card_name)):
            print("Carta ja existe.")
            continue
        else:
            break
        
    database.add_card(card_name, card_group, forca, fofura, velocidade, tamanho_dict[tamanho], idade_dict[idade], Tipo_dict[tipo], path)
    

if __name__ == "__main__":
    host = ""
    port = 25555
    if len(sys.argv) == 2:
        port = int(sys.argv[1]) 
    
    start_server(host, port)
