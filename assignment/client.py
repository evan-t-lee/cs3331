#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8

# python client.py server_IP server_port

from socket import *
import sys

import client_auth as auth

# Server would be running on the same host as Client
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

if not auth.username(clientSocket, (serverName, serverPort)):
    clientSocket.close()
    exit()
if not auth.password(clientSocket, (serverName, serverPort)):
    clientSocket.close()
    exit()

while True:
    command = input('> ')
    data, address = socket.recvfrom(2048)
    data = data.decode()
    status, message = data.split(':')
    print(message)
    if command == 'exit':
        break

clientSocket.close()
# Close the socket