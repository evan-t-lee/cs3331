# Sample code for Multi-Threaded Server
# Python 3
# Usage: python3 UDPserver3.py
# coding: utf-8

# python server.py server_port block_duration timeout

from socket import *
import threading
import time
import datetime as dt

def get_credentials():
    credentials = {}
    for line in open('credentials.txt'):
        line = line.strip().split()
        credentials[line[0]] = line[1]
    return credentials

def conn_handler(conn, clientAddress):
    while True:
        # received data from the client, now we know who we are talking with
        username = conn.recv(2048).decode()
        # get lock as we might me accessing some shared data structures
        with t_lock:
            serverMessage = 'status: valid username' if username in credentials else 'Invalid Username. Please try again'

            # send message to the client
            conn.sendto(serverMessage.encode(), clientAddress)
            # notify the thread waiting
            t_lock.notify()

            if serverMessage == 'status: valid username':
                break

    if username not in blocked_users:
        for attempts in range(2):
            # received data from the client, now we know who we are talking with
            password = conn.recv(2048).decode()
            # get lock as we might me accessing some shared data structures
            with t_lock:
                if password == credentials[username]:
                    serverMessage = 'status: authentication granted'
                elif attempts == 2:
                    serverMessage = 'Invalid Password. Your account has been blocked. Please try again later'
                    blocked_users.append(username)
                    return
                else:
                    serverMessage = 'Invalid Password. Please try again'

                # send message to the client
                conn.sendto(serverMessage.encode(), clientAddress)
                # notify the thread waiting
                t_lock.notify()

                if serverMessage == 'status: authentication granted':
                    # clients.append({
                    #         'time_logged_in': time.time(),
                    #         'last_active': time.time(),
                    #         'blocked': []
                    #     })
                    print(username, 'has logged in')
                    return


    serverMessage = 'Your account is blocked due to multiple login failures. Please try again later'
    # send message to the client
    conn.sendto(serverMessage.encode(), clientAddress)



def recv_handler():
    global t_lock
    global clientSocket
    global serverSocket
    print('Server is ready for service')

    while True:
        conn, clientAddress = serverSocket.accept()
        conn_thread = threading.Thread(name='connection', target=conn_handler, args=(conn, clientAddress))
        conn_thread.start()


def send_handler():
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    global timeout
    # go through the list of the subscribed clients and send them the current time after every 1 second
    while(1):
        # get lock
        with t_lock:
            for i in clients:
                currtime =dt.datetime.now()
                date_time = currtime.strftime('%d/%m/%Y, %H:%M:%S')
                message='Current time is ' + date_time
                clientSocket.sendto(message.encode(), i)
                print('Sending time to', i[0], 'listening at', i[1], 'at time ', date_time)
            # notify other thread
            t_lock.notify()
        # sleep for UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)

#####   CODE STARTS HERE   #####

# Server will run on this port
serverPort = 12000
t_lock=threading.Condition()

# will store clients info in this list
clients = []
blocked_users = []

# would communicate with clients after every second
UPDATE_INTERVAL= 1
timeout=False

credentials = get_credentials()

# we will use two sockets, one for sending and one for receiving
clientSocket = socket(AF_INET, SOCK_STREAM)
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)

recv_thread=threading.Thread(name='RecvHandler', target=recv_handler)
recv_thread.daemon=True
recv_thread.start()

send_thread=threading.Thread(name='SendHandler',target=send_handler)
send_thread.daemon=True
send_thread.start()
# this is the main thread
while True:
    time.sleep(0.1)
