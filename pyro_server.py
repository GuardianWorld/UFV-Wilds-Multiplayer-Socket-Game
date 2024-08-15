import Pyro5.api
import queue

@Pyro5.api.expose
class MessageServer:
    def __init__(self):
        self.response_queue = queue.Queue()

    def send_message(self, message):
        print(f"Received message: {message}")
        response = f"Server received: {message}"
        self.response_queue.put(response)  # Store the response for the client
        return "Message received, you can poll for a response."

    def get_response(self):
        if not self.response_queue.empty():
            return self.response_queue.get()
        return None  # Return None if no response is available

def main():
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(MessageServer)
    ns.register("message.server", uri)
    
    print(f"Server is running. URI: {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    main()