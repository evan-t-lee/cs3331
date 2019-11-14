import threading

def get_credentials():
    credentials = {}
    for line in open('credentials.txt'):
        line = line.strip().split()
        credentials[line[0]] = line[1]
    return credentials

def init():
    global t_lock
    t_lock = threading.Condition()

    global credentials
    credentials = get_credentials()

    global clients
    clients = []

    global blocked_users
    blocked_users = []
