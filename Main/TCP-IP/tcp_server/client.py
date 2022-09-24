import socket

HOST = 'localhost'
PORT = 9090

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket.connect((HOST, PORT))

socket.send('Hello, World!'.encode('utf-8'))

print(socket.recv(1024).decode())