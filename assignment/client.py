#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8

# python client.py server_IP server_port

import select
from socket import *
import sys
import threading
import time

import client_auth as auth

# constants
MAX_USERS = 10000

# setup client to connect with server
ip, port = sys.argv[1], int(sys.argv[2])
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((ip, port))
assigned_port = int(client_socket.recv(2048).decode())

# authenticate with server
username = auth.username(client_socket, assigned_port)
if not username:
    client_socket.close()
    exit()
if not auth.password(client_socket, assigned_port):
    client_socket.close()
    exit()

# setup socket to connect with peers
p2p_socket = socket(AF_INET, SOCK_STREAM)
p2p_socket.bind((ip, assigned_port + MAX_USERS))
p2p_socket.listen(1)

# global data
connections = {'!p2p': {'recv': p2p_socket}}
socket_store = None
logged_in = True

def recv_handler():
    global logged_in

    while True:
        data = client_socket.recv(2048).decode()

        code, response = data.split(':', 1)

        if code == 'response 22':
            print(f'> {response} < <')
            logged_in = False
            return

        # server message
        if code.startswith('response 1'):
            print(f'> {response} < <\n> ', end='')
        # private request
        elif code.startswith('response 5'):
            if code == 'response 50':
                p2p_setup_send(response)
            elif code == 'response 51':
                print(f'> {response} < <\n> ', end='')

def send_handler():
    while True:
        cmd = input('> ')
        if cmd.startswith('private '):
            try:
                user, message = cmd.split(' ', 2)[1:]
                if connections.get(user):
                    data = f'private 10:{username} (private): {message}'
                    connections[user]['send'].send(data.encode())
                else:
                    print(f'> > Error. Private messaging to {user} not enabled < <')
            except ValueError:
                print('> > Error. Usage of private is: private user message < <')
        elif cmd.startswith('stopprivate '):
            try:
                user = cmd.split(' ', 1)[1]
                if connections.get(user):
                    data = f'private 11:{username}'
                    connections[user]['send'].send(data.encode())
                    print(f'> > Private messaging with {user} has been stopped < <')
                    del connections[user]
                else:
                    print(f'> > Error. There is no private with {user} to stop < <')
            except ValueError:
                print('> > Error. Usage of stopprivate is: stopprivate user < <')
        else:
            data = f'request 20:{username}:{cmd}'
            client_socket.send(data.encode())

def p2p_handler():
    global connections

    while True:
        recv_conns = [conn['recv'] for conn in connections.values()]
        read_sockets = select.select(recv_conns, [], [])[0]

        for socket in read_sockets:
            if socket == p2p_socket:
                peer_conn, peer_addr = p2p_socket.accept()
                data = peer_conn.recv(2048).decode()

                status, data = data.split('|', 1)
                if status == 'response':
                    connections[data.split('|')[0]] = {
                        'recv': peer_conn,
                        'send': socket_store
                    }
                else:
                    p2p_setup_recv(peer_conn, data)
            else:
                data = socket.recv(2048).decode()

                if not data:
                    for user in connections:
                        if connections[user] == socket:
                            del connections[user]
                            break
                    continue

                code, response = data.split(':', 1)
                if code == 'private 10':
                    print(f'> {response} < <\n> ', end='')
                elif code == 'private 11':
                    message = f'Private messaging with {response} has been stopped'
                    print(f'> {message} < <\n> ', end='')
                    del connections[response]

def p2p_setup_recv(conn, data):
    global connections

    peer_user, peer_ip, peer_port = data.split('|')
    peer_socket = p2p_setup_port(peer_ip, peer_port)
    connections[peer_user] = {
        'recv': conn,
        'send': peer_socket
    }

    data = f'response|{username}|{ip}|{assigned_port}'
    peer_socket.send(data.encode())

    print(f'> {peer_user} started private messaging with you < <\n> ', end='')

def p2p_setup_send(data):
    global connections
    global socket_store

    peer_user, peer_ip, peer_port = data.split('|')
    socket_store = p2p_setup_port(peer_ip, peer_port)

    data = f'request|{username}|{ip}|{assigned_port}'
    socket_store.send(data.encode())

    print(f'> You started private messaging with {peer_user} < <\n> ', end='')

def p2p_setup_port(ip, port):
    peer_port = int(port) + MAX_USERS
    peer_socket = socket(AF_INET, SOCK_STREAM)
    peer_socket.connect((ip, peer_port))
    return peer_socket

recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

send_thread = threading.Thread(name='SendHandler', target=send_handler)
send_thread.daemon = True
send_thread.start()

p2p_thread = threading.Thread(name='p2pHandler', target=p2p_handler)
p2p_thread.daemon = True
p2p_thread.start()

while logged_in:
    time.sleep(0.1)

client_socket.close()
p2p_socket.close()
