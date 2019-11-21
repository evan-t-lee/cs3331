# python server.py server_port block_duration timeout

import select
from socket import *
import sys
import threading
import time

import settings
import server_auth as auth
import server_commands as command

def recv_handler():
    print('Server is ready for service')

    while True:
        with settings.t_lock:
            # Get the list sockets which are ready to be read through select
            connections = [conn['conn'] for conn in settings.auth_conns.values()] +\
                [user['conn'] for user in settings.online_users.values()] +\
                [settings.recv_socket]
            read_sockets, write_sockets, error_sockets = select.select(connections,[],[])

            for socket in read_sockets:
                # print('Changed:', socket, '\n')

                # New connection
                if socket == settings.recv_socket:
                    conn, addr = settings.recv_socket.accept()
                    conn_handler(conn, addr)
                # Some incoming message from a client
                else:
                    # Data recieved from client, process it
                    data = socket.recv(2048).decode()

                    # Force logout
                    if not data:
                        for user in settings.online_users:
                            if socket == settings.online_users[user]['conn']:
                                command.broadcast('!user', f'{user} has logged out')
                                del settings.online_users[user]
                                break

                    if data.startswith('request 1'):
                        auth.handler(data)
                    elif data.startswith('request 20'):
                        print('Received:', data, '\n')

                        if not command.handler(data):
                            data = 'response 10:Error. Invalid command'
                            conn.send(data.encode())
                        
                        # # echo
                        # data = f'response 10:{data}'
                        # socket.send(data.encode())

                # print('Online users:')
                # for item in settings.online_users:
                #     print(settings.online_users[item])
                # print('\n-------------------------------------------------------------------\n')
            settings.t_lock.notify()

def send_handler():
    # global t_lock
    global timeout
    # go through the list of the subscribed clients and send them the current time after every 1 second
    while True:
        # get lock
        with settings.t_lock:
            # notify other thread
            settings.t_lock.notify()
        # sleep for UPDATE_INTERVAL
        # time.sleep(settings.UPDATE_INTERVAL)

def conn_handler(conn, addr):
    with settings.t_lock:
        client_port = str(addr[1])
        conn.send(client_port.encode())
        settings.auth_conns[client_port] = {
            'conn': conn,
            'username': None,
            'attempts': 0
        }
        settings.t_lock.notify

#####   CODE STARTS HERE   #####

settings.data_init()
settings.server_init(sys.argv[1], sys.argv[2], sys.argv[3])

recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

send_thread = threading.Thread(name='SendHandler',target=send_handler)
send_thread.daemon = True
send_thread.start()

# this is the main thread
while True:
    time.sleep(0.1)
