# library imports
from threading import Condition
import socket

def get_credentials():
    credentials = {}
    for line in open('credentials.txt'):
        line = line.strip().split()
        credentials[line[0]] = line[1]
    return credentials

def create_user():
    return {
        'mail': [],
        'last_active': 0,
        'blocked_users': [],
        'blacklisted': False
    }

def data_init():
    global credentials
    credentials = get_credentials()

    global users
    users = {username:create_user() for username in credentials}

    global online_users
    online_users = {}

    global auth_conns
    auth_conns = {}

def server_init(port, block_duration, timeout):
    global PORT
    PORT = int(port)

    global BLOCK_DURATION
    BLOCK_DURATION = int(block_duration)

    global TIMEOUT
    TIMEOUT = int(timeout)

    global t_lock
    t_lock = Condition()

    global recv_socket
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recv_socket.bind(('localhost', PORT))
    recv_socket.listen(1)
