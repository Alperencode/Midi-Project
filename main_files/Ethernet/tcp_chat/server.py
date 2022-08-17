import socket,threading
FORMAT = 'utf-8'

class Client(threading.Thread):
    active = 0
    clients = []

    def __init__(self, server, socket, address, name):
        threading.Thread.__init__(self)
        self.server = server
        self.socket = socket
        self.address = address
        self.name = name
        self._id = Client.active + 1

        Client.active += 1
    
    def run(self):
        connected = True
        while connected:
            try:
                msg = self.socket.recv(1024).decode(FORMAT)
                if msg.lower() == "!disconnect":
                    connected = False
                    self.disconnect()
                    break
                for client in Client.clients:
                    if client._id != self._id:
                        client.socket.sendall(f"{self.name}: {msg}".encode(FORMAT))
                print(f"{self.name}: {msg}")
            except:
                connected = False
                self.disconnect()
                break

    def disconnect(self):
        Client.active -= 1
        for client in Client.clients:
            client.socket.sendall(f"{self.name} has disconnected! (Active {Client.active})".encode(FORMAT))
        print(f"{self.name} has disconnected! (Active {Client.active})")
        self.socket.close()
        Client.clients.remove(self)

def read_inport(server):
    while True:
        client, addr = server.accept()
        client.sendall(f"You are connected to chat. Type !disconnect to close the chat\nPlease enter nickname".encode(FORMAT))
        name = client.recv(1024).decode(FORMAT)

        c = Client(server, client, addr, name)
        c.start()
        Client.clients.append(c)
        print(f"{name} has connected to chat! (Active: {Client.active})")

        for client in Client.clients:
            client.socket.sendall(f"{name} has connected to chat! (Active: {Client.active})".encode(FORMAT))


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = socket.gethostbyname(socket.gethostname())
    port = input("Port (default is 9090): ")
    if port == "": port = 9090

    server.bind((host, int(port)))
    server.listen()
    print(f"Chat is started on {host}:{port}!")

    while True:
        threading.Thread(target= lambda: read_inport(server)).start()

if __name__ == '__main__':
    main()