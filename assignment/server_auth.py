# library imports
import time
# local file imports
import config
import server_commands as command

def handler(data):
    code, port, request = data.split(':')
    conn = config.auth_conns[port]['conn']
    if code == 'request 10':
        response = auth_username(port, request)
    elif code == 'request 11':
        response = auth_password(port, request)

    conn.send(response.encode())

    if code == 'request 11':
        # successful authentication
        if response.startswith('response 21'):
            auth_login(port)
        # too many attempts
        elif response.startswith('response 40'):
            auth_blacklist(port)

def auth_username(port, username):
    if not config.credentials.get(username):
        return 'response 30:Invalid Username. Please try again'
    
    if config.users[username]['blacklisted']:
        data = 'response 40:Your account is blocked due to multiple login failures. Please try again later'
        del config.auth_conns[port]
    elif config.online_users.get(username):
        data = 'response 41:Your account is already logged in'
    else:
        data = 'response 20:'
        config.auth_conns[port]['username'] = username
    return data

def auth_password(port, password):
    username = config.auth_conns[port]['username']
    if password == config.credentials[username]:
        data = 'response 21:'
    elif config.auth_conns[port]['attempts'] == 2:
        data = 'response 40:Invalid Password. Your account has been blocked. Please try again later'
    else:
        data = 'response 31:Invalid Password. Please try again'
        config.auth_conns[port]['attempts'] += 1

    return data

def auth_login(port):
    conn = config.auth_conns[port]['conn']
    username = config.auth_conns[port]['username']
    curr_time = int(time.time())

    config.users[username]['last_active'] = curr_time
    config.online_users[username] = conn

    command.broadcast(f'!{username}', f'{username} has logged in')

    for message in config.users[username]['mail']:
        conn.send(message.encode())
        # allow client to receive each message before next is sent
        time.sleep(0.1)

    config.users[username]['mail'] = []

    del config.auth_conns[port]

def auth_blacklist(port):
    username = config.auth_conns[port]['username']
    toggle_blacklist(username)
    block_timer = threading.Timer(config.BLOCK_DURATION, toggle_blacklist, [username])
    block_timer.start()
    del config.auth_conns[port]

def toggle_blacklist(sender):
    config.users[sender]['blacklisted'] = not config.users[sender]['blacklisted']
