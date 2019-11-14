import threading
import settings
import server_commands as command

def username(conn, address):
    while True:
        # received data from the client, now we know who we are talking with
        username = conn.recv(2048).decode()
        # get lock as we might me accessing some shared data structures
        with settings.t_lock:
            if username in settings.blocked_users:
                data = 'status 30:Your account is blocked due to multiple login failures. Please try again later'
            elif username in settings.credentials:
                data = 'status 10:'
            else:
                data = 'status 20:Invalid Username. Please try again'

            # send message to the client
            conn.sendto(data.encode(), address)
            # notify the thread waiting
            settings.t_lock.notify()

            if data.startswith('status 10'):
                return username

            if data.startswith('status 30'):
                return False

def password(conn, address, username):
    if username not in settings.blocked_users:
        for attempts in range(3):
            # received data from the client, now we know who we are talking with
            password = conn.recv(2048).decode()
            # get lock as we might me accessing some shared data structures
            with settings.t_lock:
                if password == settings.credentials[username]:
                    data = 'status 11:'
                elif attempts == 2:
                    data = 'status 30:Invalid Password. Your account has been blocked. Please try again later'
                    command.block_user_login(username)
                    block_timer = threading.Timer(10, command.unblock_user_login, [username])
                    block_timer.start()
                else:
                    data = 'status 21:Invalid Password. Please try again'

                conn.sendto(data.encode(), address)
                settings.t_lock.notify()

                if data.startswith('status 11'):
                    # clients.append({
                    #         'time_logged_in': time.time(),
                    #         'last_active': time.time(),
                    #         'blocked': []
                    #     })
                    command.broadcast(f'{username} logged in')
                    return True
                if data.startswith('status 30'):
                    return False
