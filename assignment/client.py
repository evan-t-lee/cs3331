#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8

# python client.py server_IP server_port

from socket import *
import sys

# Server would be running on the same host as Client
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_DGRAM)

while True:
    username = input("Username: ")

    clientSocket.sendto(username.encode(),(serverName, serverPort))
    # wait for the reply from the server
    receivedMessage, serverAddress = clientSocket.recvfrom(2048)
    receivedMessage = receivedMessage.decode()
    if receivedMessage == 'SUCCESS':
        break
        # # Wait for 10 back to back messages from server
        # for i in range(10):
        #     receivedMessage, serverAddress = clientSocket.recvfrom(2048)
        #     print(receivedMessage.decode())
    print(receivedMessage)

while True:
    password = input("Password: ")

    clientSocket.sendto(password.encode(),(serverName, serverPort))
    # wait for the reply from the server
    receivedMessage, serverAddress = clientSocket.recvfrom(2048)
    receivedMessage = receivedMessage.decode()
    if receivedMessage == 'SUCCESS':
        break
        # # Wait for 10 back to back messages from server
        # for i in range(10):
        #     receivedMessage, serverAddress = clientSocket.recvfrom(2048)
        #     print(receivedMessage.decode())
    print(receivedMessage)

print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
# prepare to exit. Send Unsubscribe message to server
message='Unsubscribe'
clientSocket.sendto(message.encode(),(serverName, serverPort))
clientSocket.close()
# Close the socket