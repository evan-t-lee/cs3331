import threading
import time
import settings
import server_commands as command

def handler(data):
    code, port, request = data.split(':')

    # print('Online users:')
    # for item in settings.online_users:
    #     print(item, settings.online_users[item])

    conn = settings.auth_conns[port]['conn']
    if code == 'request 10':
        response = auth_username(port, request)
    elif code == 'request 11':
        response = auth_password(port, request)

        # successful authentication
        if response.startswith('response 21'):
            auth_login(port)
        # too many attempts
        elif response.startswith('response 40'):
            username = settings.auth_conns[port]['username']
            command.toggle_blacklist(username)
            block_timer = threading.Timer(settings.BLOCK_DURATION, command.toggle_blacklist, [username])
            block_timer.start()
            del settings.auth_conns[port]

    conn.send(response.encode())

def auth_login(port):
    username = settings.auth_conns[port]['username']
    curr_time = time.time()

    settings.users[username]['last_active'] = curr_time

    settings.online_users[username] = {
        'conn': settings.auth_conns[port]['conn'],
        'last_active': curr_time
    }

    command.broadcast(f'!{username}', f'{username} has logged in')
    del settings.auth_conns[port]

def auth_username(port, username):
    # get lock as we might me accessing some shared data structures
    if username in settings.credentials:
        if settings.users[username]['blacklisted']:
            data = 'response 40:Your account is blocked due to multiple login failures. Please try again later'
            del settings.auth_conns[port]
        elif settings.online_users.get(username):
            data = 'response 41:Your account is already logged in'
        else:
            data = 'response 20:'
            settings.auth_conns[port]['username'] = username
    else:
        data = 'response 30:Invalid Username. Please try again'

    return data

def auth_password(port, password):
    username = settings.auth_conns[port]['username']
    if password == settings.credentials[username]:
        data = 'response 21:'
    elif settings.auth_conns[port]['attempts'] == 2:
        data = 'response 40:Invalid Password. Your account has been blocked. Please try again later'
    else:
        data = 'response 31:Invalid Password. Please try again'
        settings.auth_conns[port]['attempts'] += 1

    return data
