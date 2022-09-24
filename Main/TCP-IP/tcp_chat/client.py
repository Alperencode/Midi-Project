import socket,threading
CONNECTED = True
FORMAT = ('utf-8')

def receive(socket):
    while CONNECTED:
        msg = socket.recv(1024).decode(FORMAT)
        if msg != "": print(f"\n{msg}\n")

def main():
    global CONNECTED

    default_host = socket.gethostbyname(socket.gethostname())
    host = input(f"Host IP (default is {default_host}): ")
    if host == "": host = default_host
    port = input("Port (default is 9090): ")
    if port == "": port = 9090

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host, int(port)))
    except:
        print("Error: Could not connect to server")
        return 0

    receive_thread = threading.Thread(target=lambda: receive(server))
    receive_thread.start()

    while CONNECTED:
        msg = input("")
        if msg != "": server.send(msg.encode(FORMAT))
        if msg.lower() == "!disconnect":
            CONNECTED = False
            receive_thread.join()

if __name__ == '__main__':
    main() 