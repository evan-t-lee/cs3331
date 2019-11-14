# python server.py server_port block_duration timeout

from socket import *
import threading
import time
import datetime as dt

import settings
import server_auth as auth
import server_commands as command

def block_user_login(username):
    global blocked_users
    blocked_users.append(username)

def unblock_user_login(username):
    global blocked_users
    blocked_users.remove(username)

def conn_handler(conn, address):
    username = auth.username(conn, address)
    if not username:
        return
    if not auth.password(conn, address, username):
        return

def recv_handler():
    global serverSocket
    print('Server is ready for service')

    while True:
        conn, address = serverSocket.accept()
        conn_thread = threading.Thread(name='connection', target=conn_handler, args=(conn, address))
        conn_thread.start()


def send_handler():
    # global t_lock
    global clients
    global clientSocket
    global serverSocket
    global timeout
    # go through the list of the subscribed clients and send them the current time after every 1 second
    while True:
        # get lock
        with settings.t_lock:
            for i in settings.clients:
                currtime =dt.datetime.now()
                date_time = currtime.strftime('%d/%m/%Y, %H:%M:%S')
                message='Current time is ' + date_time
                clientSocket.sendto(message.encode(), i)
                print('Sending time to', i[0], 'listening at', i[1], 'at time ', date_time)
            # notify other thread
            settings.t_lock.notify()
        # sleep for UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)

#####   CODE STARTS HERE   #####

settings.init()

# Server will run on this port
serverPort = 12000

# would communicate with clients after every second
UPDATE_INTERVAL = 1
timeout = False

# we will use two sockets, one for sending and one for receiving
clientSocket = socket(AF_INET, SOCK_STREAM)
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)

recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

send_thread = threading.Thread(name='SendHandler',target=send_handler)
send_thread.daemon = True
send_thread.start()
# this is the main thread
while True:
    time.sleep(0.1)
