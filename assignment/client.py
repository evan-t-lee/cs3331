# library imports
from select import select
import socket
import sys
import threading
import time
# local file imports
import client_auth as auth

# constants
MAX_USERS = 10000

def recv_handler():
    while True:
        data = client_socket.recv(2048).decode()
        code, response = data.split(':', 1)

        # logout request
        if code == 'response 22':
            logout(response)
            break

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
        command = input('> ')
        # send private message
        if command.startswith('private '):
            try:
                user, message = command.split(' ', 2)[1:]
                if connections.get(user):
                    data = f'private 10:{username} (private): {message}'
                    connections[user]['send'].send(data.encode())
                else:
                    print(f'> > Error. Private messaging to {user} not enabled < <')
            except ValueError:
                print('> > Error. Invalid usage of private < <')
        # stop private messaging
        elif command.startswith('stopprivate '):
            try:
                user = command.split(' ', 1)[1]
                if connections.get(user):
                    data = f'private 11:{username}'
                    connections[user]['send'].send(data.encode())
                    print(f'> > Private messaging with {user} has been stopped < <')
                    del connections[user]
                else:
                    print(f'> > Error. There is no private with {user} to stop < <')
            except ValueError:
                print('> > Error. Invalid usage of stopprivate < <')
        # send server command
        else:
            data = f'request 20:{username}:{command}'
            client_socket.send(data.encode())

def p2p_handler():
    global connections

    while True:
        recv_conns = [conn['recv'] for conn in connections.values()]
        read_sockets = select(recv_conns, [], [])[0]

        for socket in read_sockets:
            # handle new peer connection
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
            # peer sent data
            else:
                data = socket.recv(2048).decode()
                # force logout
                if not data:
                    for user in connections:
                        if connections[user] == socket:
                            del connections[user]
                            break
                    continue

                code, response = data.split(':', 1)
                # data was message
                if code == 'private 10':
                    print(f'> {response} < <\n> ', end='')
                # data was stop request
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
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.connect((ip, peer_port))
    return peer_socket

def logout(message):
    global connections

    data = f'private 11:{username}'
    for user in [*connections.keys()]:
        if user != '!p2p':
            connections[user]['send'].send(data.encode())
            del connections[user]
    print(f'> {message} < <')
    client_socket.close()
    p2p_socket.close()


if __name__ == '__main__':
    # setup client to connect with server
    ip, port = sys.argv[1], int(sys.argv[2])
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    assigned_port = int(client_socket.recv(2048).decode())

    # authenticate with server
    username = auth.username(client_socket, assigned_port)
    if not username and not auth.password(client_socket, assigned_port):
        client_socket.close()
        exit()

    # setup socket to connect with peers
    p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p2p_socket.bind((ip, assigned_port + MAX_USERS))
    p2p_socket.listen(1)

    # global data
    connections = {'!p2p': {'recv': p2p_socket}}
    socket_store = None

    send_thread = threading.Thread(name='SendHandler', target=send_handler)
    send_thread.daemon = True
    send_thread.start()

    # start main recieving thread
    recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
    recv_thread.start()

    p2p_thread = threading.Thread(name='p2pHandler', target=p2p_handler)
    p2p_thread.daemon = True
    p2p_thread.start()
