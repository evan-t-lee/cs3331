#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8

# python client.py server_IP server_port

from socket import *
import threading
import time
import sys

import client_auth as auth

# Server would be running on the same host as Client
ip = sys.argv[1]
port= int(sys.argv[2])

send_socket = socket(AF_INET, SOCK_STREAM)
send_socket.connect((ip, port))

username = auth.username(send_socket)
if not username:
    send_socket.close()
    exit()
if not auth.password(send_socket):
    send_socket.close()
    exit()

logged_in = True

def recv_handler():
    global logged_in
    while True:
        data, address = send_socket.recvfrom(2048)
        data = data.decode()
        code, response = data.split(':', 1)
        if code == 'response 22':
            print('logging out')
            logged_in = False
            return
        elif code == 'response 10':
            print(f'{response}\n> ', end='')

def send_handler():
    while True:
        cmd = input('> ')
        if cmd:
            message = f'{username}:{cmd}'
            send_socket.send(message.encode())


send_thread = threading.Thread(name='SendHandler',target=send_handler)
send_thread.daemon = True
send_thread.start()

recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

while logged_in:
    time.sleep(0.1)

send_socket.close()