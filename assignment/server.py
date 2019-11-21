# python server.py server_port block_duration timeout

import select
from socket import *
import sys
import threading
import time

import config
import server_auth as auth
import server_commands as command

def recv_handler():
    print('Server is ready for service')

    while True:
        with config.t_lock:
            # Get the list sockets which are ready to be read through select
            connections = [config.recv_socket] +\
                [conn['conn'] for conn in config.auth_conns.values()] +\
                [user['conn'] for user in config.online_users.values()]
                
            read_sockets = select.select(connections, [], [])[0]

            for socket in read_sockets:
                # print('Changed:', socket, '\n')

                # New connection
                if socket == config.recv_socket:
                    conn, addr = config.recv_socket.accept()
                    conn_handler(conn, addr)
                # Some incoming message from a client
                else:
                    # Data recieved from client, process it
                    data = socket.recv(2048).decode()

                    # Force logout
                    if not data:
                        for user in config.online_users:
                            if socket == config.online_users[user]['conn']:
                                command.broadcast('!user', f'{user} has logged out')
                                del config.online_users[user]
                                break
                        continue

                    if data.startswith('request 1'):
                        auth.handler(data)
                    elif data.startswith('request 20'):
                        command.handler(data)

            config.t_lock.notify()

def conn_handler(conn, addr):
    print(addr)
    with config.t_lock:
        client_port = str(addr[1])
        conn.send(client_port.encode())
        config.auth_conns[client_port] = {
            'conn': conn,
            'username': None,
            'attempts': 0
        }
        config.t_lock.notify

#####   CODE STARTS HERE   #####

config.data_init()
config.server_init(sys.argv[1], sys.argv[2], sys.argv[3])

recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

# this is the main thread
while True:
    time.sleep(0.1)
