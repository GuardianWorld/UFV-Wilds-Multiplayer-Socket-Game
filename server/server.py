import sys
import socket
import json
import threading
import time
import datetime
import signal

import database
from config import active_connections, stop_event, logged_users

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
    except KeyboardInterrupt:
        print("\n[*] Keyboard interruption.")
    except Exception as e:
        print(f"Error: {e}")

    print("[*] Server terminal stopped.")

#Server-Client Side

def handle_client(client_socket, client_address):        
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
        print(f"[*] Connection closed from: {client_address[0]}:{client_address[1]}")

def handle_response(data, client_address):

    message = data.get('message')
    command = data.get('command')
    token = data.get('token')
    response = {}

    if(command != "ping"):
        print(f"[*] Received: {message}")

    if(command == "ping"):
        response = {"status": 200, "message": "pong", "command": "pong"}
    elif(command == "logoff"):
        response = {"status": 200, "message": "Goodbye!", "command": "logoff"}
    elif(command == "chat"):
        response = {"status": 200, "message": message, "command": "chat"}
    elif(command == "register"):
        response = register(data.get('username'), data.get('password'), client_address)
    elif(command == "login"):
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



if __name__ == "__main__":
    host = ""
    port = 25555
    if len(sys.argv) == 2:
        port = int(sys.argv[1]) 
    
    start_server(host, port)
