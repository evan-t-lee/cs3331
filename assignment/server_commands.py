import time
import settings

def handler(data):
    code, sender, data = data.split(':', 2)
    data = data.split()
    cmd = data[0]

    settings.users[sender]['last_active'] = time.time()
    if cmd in commands:
        if len(data) > 1:
            commands[cmd](sender, data[1])
        else:
            commands[cmd](sender)
        return True
    return False

def toggle_blacklist(sender):
    settings.users[sender]['blacklisted'] = not settings.users[sender]['blacklisted']

# def message():

def broadcast(sender, message):
    print('broadcasting', sender)
    if sender.startswith('!'):
        sender = sender[1:]
        data = f'response 10:[broadcast] {message}'
    else:
        data = f'response 10:[broadcast] {sender}: {message}'

    users = [user for user in settings.online_users if valid_user(sender, user)]
    for user in users:
        settings.online_users[user]['conn'].send(data.encode())

def whoelse(sender):
    users = [user for user in settings.online_users if user != sender]
    data = f'response 10:Online: {", ".join(users)}'
    settings.online_users[sender]['conn'].send(data.encode())

def whoelsesince(sender, time_since):
    curr_time = time.time()
    users_since = [user for user in settings.users if user != sender]
    for user in users_since:
        if curr_time - settings.users[user]['last_active'] > int(time_since):
            users_since.remove(user)

    data = f'response 10:Online since {time_since}s ago: {", ".join(users_since)}'
    settings.online_users[sender]['conn'].send(data.encode())

def block(sender, user):
    if sender == user:
        data = f'response 10:Error. Cannot block self'
    elif not settings.users.get(user):
        data = f'response 10:Error. {user} does not exist'
    elif user not in settings.users[sender]['blocked_users']:
        settings.users[sender]['blocked_users'].append(user)
        data = f'response 10:{user} has been blocked'
    else:
        data = f'response 10:Error. {user} is already blocked'

    settings.online_users[sender]['conn'].send(data.encode())

def unblock(sender, user):
    if sender == user:
        data = f'response 10:Error. Cannot unblock self'
    elif not settings.users.get(user):
        data = f'response 10:Error. {user} does not exist'
    elif user in settings.users[sender]['blocked_users']:
        settings.users[sender]['blocked_users'].remove(user)
        data = f'response 10:{user} has been unblocked'
    else:
        data = f'response 10:Error. {user} is not blocked'

    settings.online_users[sender]['conn'].send(data.encode())

def logout(sender):
    data = 'response 22:You have logged out'
    settings.online_users[sender]['conn'].send(data.encode())
    del settings.online_users[sender]

    broadcast(f'!{sender}', f'{sender} has logged out')

def valid_user(sender, user):
    return user != sender and sender not in settings.users[user]['blocked_users']

commands = {
    'broadcast': broadcast,
    'whoelse': whoelse,
    'whoelsesince': whoelsesince,
    'block': block,
    'unblock': unblock,
    'logout': logout
}