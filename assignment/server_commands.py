# library imports
import time
# local file import
import config

def handler(data):
    sender, data = data.split(':', 2)[1:]
    # determine command and arguments
    try:
        cmd, args = data.split(' ', 1)
        args = [sender, args]
    except ValueError:
        cmd = data
        args = [sender]

    config.users[sender]['last_active'] = time.time()

    # run if valid command
    if commands.get(cmd):
        try:
            commands[cmd](*args)
        except TypeError:
            data = f'response 12:Error. Invalid usage of {cmd}'
            config.online_users[sender].send(data.encode())
    else:
        data = 'response 12:Error. Invalid command'
        config.online_users[sender].send(data.encode())

def message(sender, data):
    try:
        user, message = data.split(' ', 1)
    except ValueError:
        raise TypeError from None

    message = message.strip()
    if not message:
        raise TypeError

    if not config.users.get(user):
        data = f'response 12:Error. User {user} does not exist'
    elif sender == user:
        data = f'response 12:Error. Cannot message yourself'
    elif sender in config.users[user]['blocked_users']:
        data = f'response 12:Your message could not be delivered as {user} has blocked you'
    else:
        if config.online_users.get(user):
            data = f'response 10:{sender}: {message}'
        else:
            data = f'response 11:{sender}: {message}'
    
    # send user message
    if data.startswith('response 10'):
        config.online_users[user].send(data.encode())
    # store user message
    elif data.startswith('response 11'):
        config.users[user]['mail'].append(data)
    else:
        config.online_users[sender].send(data.encode())

def broadcast(sender, message):
    if sender.startswith('!'):
        sender = sender[1:]
        data = f'response 10:[broadcast] {message}'
    else:
        data = f'response 10:[broadcast] {sender}: {message}'

    # broadcast non-sender, unblocked users
    users = [user for user in config.online_users if valid_user(sender, user)]
    for user in users:
        config.online_users[user].send(data.encode())

    if len(users) + 1 < len(config.online_users):
        data = f'response 10:Your message could not be delivered to some recipients'
        config.online_users[sender].send(data.encode())

def whoelse(sender):
    users = [user for user in config.online_users if user != sender]
    data = f'response 10:Online: {", ".join(users)}'
    config.online_users[sender].send(data.encode())

def whoelsesince(sender, time_since):
    users_since = []
    for user in config.users:
        if user != sender and was_online_since(user, int(time_since)):
            users_since.append(user)

    data = f'response 10:Online since {time_since}s ago: {", ".join(users_since)}'
    config.online_users[sender].send(data.encode())

def block(sender, user):
    if sender == user:
        data = 'response 12:Error. Cannot block yourself'
    elif not config.users.get(user):
        data = f'response 12:Error. User {user} does not exist'
    elif user not in config.users[sender]['blocked_users']:
        config.users[sender]['blocked_users'].append(user)
        data = f'response 10:User {user} has been blocked'
    else:
        data = f'response 12:Error. User {user} is already blocked'

    config.online_users[sender].send(data.encode())

def unblock(sender, user):
    if sender == user:
        data = 'response 12:Error. Cannot unblock yourself'
    elif not config.users.get(user):
        data = f'response 12:Error. User {user} does not exist'
    elif user in config.users[sender]['blocked_users']:
        config.users[sender]['blocked_users'].remove(user)
        data = f'response 10:User {user} has been unblocked'
    else:
        data = f'response 12:Error. User {user} is not blocked'

    config.online_users[sender].send(data.encode())

def logout(sender):
    data = 'response 22:You have logged out'
    config.online_users[sender].send(data.encode())
    broadcast(f'!{sender}', f'{sender} has logged out')
    del config.online_users[sender]

def startprivate(sender, user):
    if sender == user:
        data = 'response 12:Error. Cannot start private with yourself'
    elif not config.users.get(user):
        data = f'response 12:Error. User {user} does not exist'
    elif not config.online_users.get(user):
        data = f'response 12:Error. Could not start private as {user} is not online'
    elif sender in config.users[user]['blocked_users']:
        data = f'response 12:Error. Could not start private as {user} has blocked you'
    else:
        addr = config.online_users[user].getpeername()
        data = f'response 50:{user}|{addr[0]}|{addr[1]}'

    config.online_users[sender].send(data.encode())

def valid_user(sender, user):
    return user != sender and sender not in config.users[user]['blocked_users']

def was_online_since(user, time_since):
    now = int(time.time())
    return config.online_users.get(user) or now - config.users[user]['last_active'] <= time_since

commands = {
    'message': message,
    'broadcast': broadcast,
    'whoelse': whoelse,
    'whoelsesince': whoelsesince,
    'block': block,
    'unblock': unblock,
    'logout': logout,
    'startprivate': startprivate
}
