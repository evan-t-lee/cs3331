#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8

# python client.py server_IP server_port

from socket import *
import sys

import auth as auth

# Server would be running on the same host as Client
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

if not auth.username(clientSocket, (serverName, serverPort)):
    exit()
if not auth.password(clientSocket, (serverName, serverPort)):
    exit()

print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
# prepare to exit. Send Unsubscribe message to server
clientSocket.close()
# Close the socket