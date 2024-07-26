import base64
import multiprocessing
import select
import string
import threading
import json
import socket
import sys
from time import sleep

stop_event = multiprocessing.Event()

def close_connection(client_socket):
    print("[*] Disconnected from server.")
    client_socket.close()

def is_alive(client_socket):
    timeout = 1
    tries = 0
    while not stop_event.is_set():
        try:
            client_socket.settimeout(timeout)
            message = json.dumps({"token": "none", "message": "ping", "command": "ping"})
            client_socket.send(message.encode())
            response = client_socket.recv(1024)
            client_socket.settimeout(None)
            tries = 0
            sleep(3.0)
        except socket.timeout:
            if(tries == 3):
                print("\n[*] Connection Lost.")
                stop_event.set()
                break
            print("[*] Server not responding, retrying {}/3".format(tries))
            tries += 1
            continue
        except BrokenPipeError:
            print("\n[*] Connection Lost.")
            stop_event.set()
            break
        except Exception as e:
            print(f"\nError: {e}")
            stop_event.set()
            break

def package_message(message, token="none"):
    full_message = message.split(' ', 1)
    command = full_message[0]
    json_message = {}
    send_status = True

    try:
        if(command == "exit"):
            json_message = {"token": token, "message": message, "command": "logoff"}
        elif(command == "register"):
            send_status, json_message = register(message, token)
        elif(command == "login"):
            send_status, json_message = login(message, token)
        else:
            json_message = {"token": token, "message": message, "command": "chat"}
    except Exception as e:
                json_message = {"token": token, "message": f"Error: {str(e)}", "command": "error"}
                send_status = False

    return send_status, json_message

def handle_response(_data):
    data = json.loads(_data)
    status = data.get('status')
    message = data.get('message')
    command = data.get('command')
    #print(f"[*] {status} : {message} : {command}")
    print(f"[*] {message}")

    if(command == "login"):
        token = data.get('token')
        #print(token)
        return command, token
    
    return command, message

def client_handler(client_socket):
    token = ""
    username = ""
    try:
        if(username):
            print(f"[*] Logged in as {username}")
        print("Enter a message: ", end='', flush=True)
        while not stop_event.is_set():
            ready, _, _ = select.select([sys.stdin], [], [], 1)
            if ready:
                message = sys.stdin.readline().strip()
                if(message):
                    send_status, packed_message = package_message(message, token)
                    if not send_status:
                        print(f"[*] {packed_message.get('message')}")
                        print("Enter a message: ", end='', flush=True)
                        continue
                    package = json.dumps(packed_message)
                    client_socket.send(package.encode())

                    response = client_socket.recv(2048)
                    response = response.decode()
                    command, data = handle_response(response)


                    if(command == "login"):
                        token = data
                        username = packed_message.get('username')
                    if(message == "exit"):
                        stop_event.set()
                        break
                    print("Enter a message: ", end='', flush=True)
    except KeyboardInterrupt:
        print("\n[*] User interruption.")
    except Exception as e:
        print(f"Error: {e}")


#Start Client
def start_client(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print(f"[*] Connection refused to {host}:{port}")
        return
    print(f"[*] Connected to {host}:{port}")


    alive_process = multiprocessing.Process(target=is_alive, args=(client_socket,))
    alive_process.start()
    client_handler_tread = threading.Thread(target=client_handler, args=(client_socket,))
    client_handler_tread.start()


    while not stop_event.is_set() and client_handler_tread.is_alive():
        sleep(1)

    
    if(client_handler_tread.is_alive()):
        client_handler_tread.join()
    
    alive_process.join()
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


if __name__ == "__main__":
    host = "localhost"
    port = 25555
    if(len(sys.argv) == 3):
        host = sys.argv[1]
        port = int(sys.argv[2])
    start_client(host, port)

