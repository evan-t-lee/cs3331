# library imports
from select import select
import sys
import threading
import time
# local file imports
import config
import server_auth as auth
import server_commands as command

def recv_handler():
    print('Server is ready for service')

    while True:
        with config.t_lock:
            connections = [config.recv_socket] + [*config.online_users.values()] +\
                [conn['conn'] for conn in config.auth_conns.values()]
                
            read_sockets = select(connections, [], [])[0]

            for socket in read_sockets:
                # handle new client connection
                if socket == config.recv_socket:
                    conn, addr = config.recv_socket.accept()
                    conn_handler(conn, addr)
                # client sent data
                else:
                    data = socket.recv(2048).decode()
                    # force logout
                    if not data:
                        for user in config.online_users:
                            if socket == config.online_users[user]:
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
    with config.t_lock:
        client_port = str(addr[1])
        conn.send(client_port.encode())
        config.auth_conns[client_port] = {
            'conn': conn,
            'username': None,
            'attempts': 0
        }
        config.t_lock.notify

def timeout_handler():
    while True:
        curr_time = int(time.time())
        timed_out_users = []
        for user in config.online_users.keys():
            if curr_time - config.users[user]['last_active'] > config.TIMEOUT:
                timed_out_users.append(user)

        for user in timed_out_users:
            data = 'response 22:You have timed out'
            config.online_users[user].send(data.encode())
            command.broadcast(f'!{user}', f'{user} has timed out')
            del config.online_users[user]

        # As we use integers for time, check every second
        time.sleep(1)


if __name__ == '__main__':
    config.data_init()
    config.server_init(sys.argv[1], sys.argv[2], sys.argv[3])

    # start main recieving thread
    recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
    recv_thread.start()

    timeout_thread = threading.Thread(name='TimeoutHandler', target=timeout_handler)
    timeout_thread.daemon = True
    timeout_thread.start()
