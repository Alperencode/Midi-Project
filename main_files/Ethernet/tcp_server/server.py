import socket

HOST = 'localhost'
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))

server.listen(5)

while True:
    client, addr = server.accept()
    print(f'Connected to {addr}')
    msg = client.recv(1024).decode()
    print(f'from {addr}, Received: {msg}')
    client.send('Hello, World!'.encode('utf-8'))
    client.close()
    print(f"Closed connection to {addr}")