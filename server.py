import sys
import socket
import json
import threading
import time
import signal
import sqlite3

import database

active_connections = []
active_sockets = []
stop_event = threading.Event()

#Signal Handling
def signal_handler(sig, frame):
    print(f"[*] Signal received: {sig}. Shutting down...")
    shutdown_server(3)

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
    server_socket.close()

#Shutdown Server
def shutdown_server(timeout=5):
    print(f"[*] Shutting down server in {timeout} seconds.")
    stop_event.set()
    time.sleep(timeout)
    for active_socket in active_sockets:
        active_socket.close()
    sys.exit(0)
    


#Server-Client Side

def handle_client(client_socket, client_address):        
    print(f"[*] Accepted connection from: {client_address[0]}:{client_address[1]}")
    active_connections.append(client_address)
    active_sockets.append(client_socket)
    #time.time()
    if not client_socket:
        return
    
    client_socket.settimeout(5.0)
    
    try:
        while not stop_event.is_set():
            try:
                request = client_socket.recv(1024)
                if not request:
                    break
                message = request.decode()
                response = json.dumps(handle_response(message))
                client_socket.send(response.encode())
            except socket.timeout:
                continue
    except Exception as e:
        print(f"Error: {e}")
    finally:
        active_sockets.remove(client_socket)
        client_socket.close()
        active_connections.remove(client_address)
        print(f"[*] Connection closed from: {client_address[0]}:{client_address[1]}")

def handle_response(_data):

    data = json.loads(_data)
    message = data.get('message')
    command = data.get('command')
    token = data.get('token')

    if(command != "ping"):
        print(f"[*] Received: {message}")

    if(command == "ping"):
        #print("ping")
        return {"status": 200, "message": "pong", "command": "pong"}
    elif(command == "logoff"):
        return {"status": 200, "message": "Goodbye!", "command": "logoff"}
    elif(command == "chat"):
        return {"status": 200, "message": message, "command": "chat"}
    elif(command == "register"):
        username = data.get('username')
        password = data.get('password')
        return database.add_user(username, password)
    elif(command == "login"):
        username = data.get('username')
        password = data.get('password')
        return database.login_user(username, password)
    else:
        return {"status": 401, "message": "Invalid Command", "command": "none"}


#Internal Server Side
def internal_server_terminal():
    print("[*] Server terminal started.")
    try:
        while not stop_event.is_set():
            command = input("")
            if command == "shutdown":
                shutdown_server()
            if command == "status":
                number_of_sockets = len(active_sockets)
                print("[*] Server is running.")
                print(f"[*] Number of sockets open: {number_of_sockets}")
                print(f"[*] Active connections: ")
                for connection in active_connections:
                    print(f" >> {connection[0]}:{connection[1]}")

    except KeyboardInterrupt:
        print("\n[*] Keyboard interruption.")
    except Exception as e:
        print(f"Error: {e}")

    print("[*] Server terminal stopped.")


if __name__ == "__main__":
    host = ""
    port = 25556
    if len(sys.argv) == 2:
        port = int(sys.argv[1]) 
    
    start_server(host, port)
