import threading
import time
import settings
import server_commands as command

def username(conn):
    while True:
        # received data from the client, now we know who we are talking with
        username = conn.recv(2048).decode()
        # get lock as we might me accessing some shared data structures
        with settings.t_lock:
            if username in settings.credentials:
                if settings.users[username]['blacklisted']:
                    data = 'status 40:Your account is blocked due to multiple login failures. Please try again later'
                else:
                    data = 'status 20:'
            else:
                data = 'status 30:Invalid Username. Please try again'

            # send message to the client
            conn.send(data.encode())
            # notify the thread waiting
            settings.t_lock.notify()

            if data.startswith('status 20'):
                return username

            if data.startswith('status 40'):
                return False

def password(conn, username):
    for attempts in range(3):
        # received data from the client, now we know who we are talking with
        password = conn.recv(2048).decode()
        # get lock as we might me accessing some shared data structures
        with settings.t_lock:
            if password == settings.credentials[username]:
                data = 'status 21:'
            elif attempts == 2:
                data = 'status 40:Invalid Password. Your account has been blocked. Please try again later'
                command.toggle_blacklist(username)
                block_timer = threading.Timer(settings.BLOCK_DURATION, command.toggle_blacklist, [username])
                block_timer.start()
            else:
                data = 'status 31:Invalid Password. Please try again'

            conn.send(data.encode())
            settings.t_lock.notify()

            if data.startswith('status 21'):
                    # {
                    #     'time_logged_in': time.time(),
                    #     'last_active': time.time(),
                    #     'blocked': []
                    # }
                command.broadcast(username, f'{username} has logged in')
                settings.online_users[username] = {
                    'conn': conn,
                    'time_logged_in': time.time(),
                    'last_active': time.time()
                }
                return True
            if data.startswith('status 40'):
                return False
