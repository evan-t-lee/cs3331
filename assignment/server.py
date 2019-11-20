# python server.py server_port block_duration timeout

import select
from socket import *
import sys
import threading
import time

import settings
import server_auth as auth
import server_commands as command

def conn_handler():
    while True:
        with settings.t_lock:
            # Get the list sockets which are ready to be read through select
            connections = [*settings.auth_conns.keys()] + [settings.recv_socket]
            read_sockets, write_sockets, error_sockets = select.select(connections,[],[])

            for socket in read_sockets:
                if socket == settings.recv_socket:
                    # Handle the case in which there is a new connection recieved through server_socket
                    conn, addr = settings.recv_socket.accept()
                    print('new client connected')
                    settings.auth_conns[conn] = {
                        'username': None,
                        'attempts': 0
                    }
                else:
                    data = socket.recv(2048).decode()
                    auth.handler(conn, data)

def recv_handler():
    print('Server is ready for service')

    while True:
        with settings.t_lock:
            # Get the list sockets which are ready to be read through select
            connections = [details['conn'] for user, details in settings.online_users.items()]
            print('conns: ',connections)
            read_sockets, write_sockets, error_sockets = select.select(connections,[],[])

            for socket in read_sockets:
                print('Changed:', socket, '\n')

                # Data recieved from client, process it
                data = socket.recv(2048).decode()
                username, request = data.split(':', 1) 

                if not data:
                    print('logging out')
                    del settings.online_users[username]

                command.handler(username, data)

                print('Received:', data, '\n')

                # echo
                data = f'response 10:{request}'
                socket.send(data.encode())

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

#####   CODE STARTS HERE   #####

settings.data_init()
settings.server_init(sys.argv[1], sys.argv[2], sys.argv[3])

conn_thread = threading.Thread(name='ConnHandler', target=conn_handler)
conn_thread.daemon = True
conn_thread.start()

recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

send_thread = threading.Thread(name='SendHandler',target=send_handler)
send_thread.daemon = True
send_thread.start()

# this is the main thread
while True:
    time.sleep(0.1)
