from socket import *
import threading

def get_credentials():
    credentials = {}
    for line in open('credentials.txt'):
        line = line.strip().split()
        credentials[line[0]] = line[1]
    return credentials

def create_user():
    return {
        'socket': None,
        'mail': [],
        'blocked_users': [],
        'blacklisted': False
    }

def server_init(port, block_duration, timeout):
    global UPDATE_INTERVAL
    UPDATE_INTERVAL = 1

    global PORT
    PORT = int(port)

    global BLOCK_DURATION
    BLOCK_DURATION = int(block_duration)

    global TIMEOUT
    TIMEOUT = int(timeout)

    global t_lock
    t_lock = threading.Condition()

    # we will use two sockets, one for sending and one for receiving
    global serverSocket
    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(('localhost', PORT))
    serverSocket.listen(1)

    global clientSocket
    clientSocket = socket(AF_INET, SOCK_STREAM)

def data_init():
    global credentials
    credentials = get_credentials()

    global users
    users = {username:create_user() for username in credentials}

    global online_users
    online_users = {}
