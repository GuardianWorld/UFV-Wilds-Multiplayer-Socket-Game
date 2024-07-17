import sys
import socket
import json
import threading
import time

active_connections = []

#Start Server
def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[*] Listening on {host}:{port}")
    while True:
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address,))
        client_handler.start()

#Shutdown Server
def shutdown_server():
    print("[*] Shutting down server.")
    exit(0)




#Server-Client Side

def handle_client(client_socket, client_address):        
    print(f"[*] Accepted connection from: {client_address[0]}:{client_address[1]}")
    active_connections.append(client_address)
    print(f"[*] Active connections: {active_connections}")
    #time.time()
    if not client_socket:
        return
    
    try:
        while True:
            request = client_socket.recv(1024)
            if not request:
                break
            message = request.decode()
            response = handle_response(message)
            client_socket.send(json.dumps(response).encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        active_connections.remove(client_address)
        print(f"[*] Connection closed from: {client_address[0]}:{client_address[1]}")

def handle_response(message):

    if(message == "ping"):
        print("ping")
        return {"status": 200}
    

    print(f"[*] Received: {message}")
    
    if(message == "exit"):
        return {"status": 200, "message": "Goodbye!"}
    else:
        return {"status": 200, "message": "Message received,", "data": message}


#Internal Server Side
def internal_server_terminal():
    while True:
        command = input("Enter a message: ")
        if command == "shutdown":
            shutdown_server()
        if command == "status":
            number_of_sockets = len(threading.enumerate())
            print("Server is running.")
            print("Number of sockets open:", number_of_sockets)

if __name__ == "__main__":
    host = ""
    port = 25556
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    
    start_server(host, port)
