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

if not auth.username(send_socket):
    send_socket.close()
    exit()
if not auth.password(send_socket):
    send_socket.close()
    exit()

logged_in = True
recv_socket = socket(AF_INET, SOCK_STREAM)
recv_socket.connect((ip, port))

def recv_handler():
    global logged_in
    while True:
        data, address = send_socket.recvfrom(2048)
        data = data.decode()
        status, message = data.split(':')
        if status == 'status 22':
            print('logging out')
            logged_in = False
            return
        print(message)

def send_handler():
    while True:
        cmd = input('> ')
        if cmd:
            send_socket.send(cmd.encode())


send_thread = threading.Thread(name='SendHandler',target=send_handler)
send_thread.daemon = True
send_thread.start()

recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

while logged_in:
    time.sleep(0.1)