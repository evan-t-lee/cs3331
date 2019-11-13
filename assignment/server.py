# Sample code for Multi-Threaded Server
# Python 3
# Usage: python3 UDPserver3.py
# coding: utf-8

# python server.py server_port block_duration timeout

from socket import *
import threading
import time
import datetime as dt

# Server will run on this port
serverPort = 12000
t_lock=threading.Condition()
# will store clients info in this list
clients = []
client_info = ['yoda']
# would communicate with clients after every second
UPDATE_INTERVAL= 1
timeout=False


def recv_handler():
    global t_lock
    global clientSocket
    global serverSocket
    print('Server is ready for service')

    while True:
        data, clientAddress = serverSocket.recvfrom(2048)
        # received data from the client, now we know who we are talking with
        username = data.decode()
        # get lock as we might me accessing some shared data structures
        with t_lock:
            currtime = dt.datetime.now()
            date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")
            print('Received request from', username, clientAddress[0], 'listening at', clientAddress[1], ':',  'at time ', date_time)
            
            serverMessage = "SUCCESS" if username in client_info else "Invalid Password. Please try again"

            # send message to the client
            serverSocket.sendto(serverMessage.encode(), clientAddress)
            # notify the thread waiting
            t_lock.notify()

            if serverMessage == "SUCCESS":
                break

    while True:
        data, clientAddress = serverSocket.recvfrom(2048)
        # received data from the client, now we know who we are talking with
        password = data.decode()
        # get lock as we might me accessing some shared data structures
        with t_lock:
            
            serverMessage = "SUCCESS" if password == client_info[username] else "Invalid Password. Please try again"

            # send message to the client
            serverSocket.sendto(serverMessage.encode(), clientAddress)
            # notify the thread waiting
            t_lock.notify()

            if serverMessage == "SUCCESS":
                break


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
                date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")
                message='Current time is ' + date_time
                clientSocket.sendto(message.encode(), i)
                print('Sending time to', i[0], 'listening at', i[1], 'at time ', date_time)
            # notify other thread
            t_lock.notify()
        # sleep for UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)

# we will use two sockets, one for sending and one for receiving
clientSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('localhost', serverPort))

recv_thread=threading.Thread(name="RecvHandler", target=recv_handler)
recv_thread.daemon=True
recv_thread.start()

send_thread=threading.Thread(name="SendHandler",target=send_handler)
send_thread.daemon=True
send_thread.start()
# this is the main thread
while True:
    time.sleep(0.1)
