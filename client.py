import multiprocessing
import select
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
            client_socket.send("ping".encode())
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

def client_handler(client_socket):
    try:
        print("Enter a message: ", end='', flush=True)
        while not stop_event.is_set():
            ready, _, _ = select.select([sys.stdin], [], [], 1)
            if ready:
                message = sys.stdin.readline().strip()
                if(message):
                    client_socket.send(message.encode())
                    response = client_socket.recv(1024)
                    print(f"Received: {response}")
                    if(message == "exit"):
                        stop_event.set()
                        break
                print("Enter a message: ", end='', flush=True)
    except KeyboardInterrupt:
        print("\n[*] User interruption.")
    except Exception as e:
        print(f"Error: {e}")


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
        pass

    
    if(client_handler_tread.is_alive()):
        client_handler_tread.join()
    
    alive_process.join()
    close_connection(client_socket)
        

if __name__ == "__main__":
    host = "localhost"
    port = 25556
    if(len(sys.argv) == 3):
        host = sys.argv[1]
        port = int(sys.argv[2])
    start_client(host, port)

