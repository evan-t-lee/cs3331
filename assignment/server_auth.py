import threading
import time
import settings
import server_commands as command

def handler(conn, data):
    code, request = data.split(':')

    # print('Online users:')
    # for item in settings.online_users:
    #     print(item, settings.online_users[item])

    if code == 'request 10':
        response = auth_username(conn, request)
    elif code == 'request 11':
        response = auth_password(conn, request)
        if response.startswith('response 40'):
            username = settings.auth_conns[conn]['username']
            command.toggle_blacklist(username)
            block_timer = threading.Timer(settings.BLOCK_DURATION, command.toggle_blacklist, [username])
            block_timer.start()
            del settings.auth_conns[conn]

    conn.send(response.encode())


def auth_username(conn, username):
    # get lock as we might me accessing some shared data structures
    with settings.t_lock:
        if username in settings.credentials:
            if settings.users[username]['blacklisted']:
                data = 'response 40:Your account is blocked due to multiple login failures. Please try again later'
                del settings.auth_conns[conn]
            else:
                data = 'response 20:'
                settings.auth_conns[conn]['username'] = username
        else:
            data = 'response 30:Invalid Username. Please try again'

        # notify the thread waiting
        settings.t_lock.notify()

        return data

def auth_password(conn, password):
    # get lock as we might me accessing some shared data structures
    with settings.t_lock:
        username = settings.auth_conns[conn]['username']
        if password == settings.credentials[username]:
            data = 'response 21:'

            del settings.auth_conns[conn]

            settings.online_users[username] = {
                'conn': conn,
                'time_logged_in': time.time(),
                'last_active': time.time()
            }

            command.broadcast(username, f'{username} has logged in')
        elif settings.online_users[conn]['attempts'] == 2:
            data = 'response 40:Invalid Password. Your account has been blocked. Please try again later'
        else:
            data = 'response 31:Invalid Password. Please try again'
            settings.auth_conns[conn]['attempts'] += 1

        settings.t_lock.notify()

        return data
