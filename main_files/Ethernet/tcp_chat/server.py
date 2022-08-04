# Didn't complete yet
import socket,threading

class Client(threading.Thread):
    connections = []
    _id = 0

    def __init__(self, socket, address):
        self.__socket = socket
        self.__address = address

        _id += 1


def read_inport(server):
    while True:
        client, addr = server.accept()
        Client.connections.append(Client(client, addr))
        client.send(f"You are connected to chat with {Client._id} id".encode('utf-8'))


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = input("Host IP (default is localhost): ")
    if host == "": host = "localhost"

    port = int(input("Port (default is 9090): "))
    if port == 0: port = 9090

    server.bind((host, port))
    server.listen(5)


