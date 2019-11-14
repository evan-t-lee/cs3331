# python server.py server_port block_duration timeout

from socket import *
import threading
import time
import sys
import datetime as dt

import settings
import server_auth as auth
import server_commands as command

def recv_handler():
    print('Server is ready for service')

    while True:
        conn, address = settings.serverSocket.accept()
        conn_thread = threading.Thread(name='connection', target=conn_handler, args=(conn, address))
        conn_thread.start()

def send_handler():
    # global t_lock
    global timeout
    # go through the list of the subscribed clients and send them the current time after every 1 second
    while True:
        # get lock
        with settings.t_lock:
            # for i in settings.clients:
            #     currtime =dt.datetime.now()
            #     date_time = currtime.strftime('%d/%m/%Y, %H:%M:%S')
            #     message='Current time is ' + date_time
            #     .sendto(message.encode(), i)
            #     print('Sending time to', i[0], 'listening at', i[1], 'at time ', date_time)
            # # notify other thread
            settings.t_lock.notify()
        # sleep for UPDATE_INTERVAL
        time.sleep(settings.UPDATE_INTERVAL)

def conn_handler(conn, address):
    username = auth.username(conn, address)
    if not username:
        return
    if not auth.password(conn, address, username):
        return
    # cmd_handler(conn)

# def cmd_handler(conn):
#     while True:
#         cmd = conn.recv(2048).decode()
#         with settings.t_lock:


#####   CODE STARTS HERE   #####

settings.server_init(sys.argv[1], sys.argv[2], sys.argv[3])
settings.data_init()

recv_thread = threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon = True
recv_thread.start()

send_thread = threading.Thread(name='SendHandler',target=send_handler)
send_thread.daemon = True
send_thread.start()

# this is the main thread
while True:
    time.sleep(0.1)
