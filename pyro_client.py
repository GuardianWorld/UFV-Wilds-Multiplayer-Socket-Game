import Pyro5.api
import threading
import time

def send_messages():
    ns = Pyro5.api.locate_ns()                            # Locate the Pyro nameserver in this thread
    uri = ns.lookup("message.server")             # Look up the URI by name
    server = Pyro5.api.Proxy(uri)                         # Create a new proxy for the remote object
    
    while True:
        msg = input("Enter message to send to server: ")
        response = server.send_message(msg)
        print(f"Server response: {response}")

def listen_for_responses():
    ns = Pyro5.api.locate_ns()
    uri = ns.lookup("message.server")
    server = Pyro5.api.Proxy(uri)

    while True:
        response = server.get_response()  # Poll the server for a new response
        if response:
            print(f"Received from server: {response}")
        time.sleep(1)  # Poll every second to avoid busy waiting

def main():
    ns = Pyro5.api.locate_ns()                            # Locate the Pyro nameserver
    uri = ns.lookup("message.server")             # Look up the URI by name
    server = Pyro5.api.Proxy(uri)                         # Create a proxy for the remote object

    # Thread to handle sending messages
    send_thread = threading.Thread(target=send_messages)
    
    # Thread to handle listening to responses
    listen_thread = threading.Thread(target=listen_for_responses)

    send_thread.start()
    listen_thread.start()

    send_thread.join()
    listen_thread.join()

if __name__ == "__main__":
    main()