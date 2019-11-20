import settings

def handler(sender, data):
    data = data.split(' ', 1)
    cmd = data[0]
    print(data)
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
    print('broadcasting')
    data = f'response 10:[broadcast] {message}'
    for user in settings.online_users:
        # check if logged in and not blocked
        if user != sender and user not in settings.users[sender]['blocked_users']:
            settings.online_users[user]['conn'].send(data.encode())

def whoelse(sender):
    users = [user['username'] for conn, user in settings.online_users.items() if conn != sender]
    print('Online users:' ,', '.join(users))

# def whoelsesince(conn, time_since):
#     curr_time = time.time()
#     for username in settings.online_users:
#         if username != conn:
#             if curr_time - settings.online_users[username]['time_logged_in'] < time_since:
#                 print(username)

# def block():

# def unblock():

def logout(sender):
    username = settings.online_users[sender]['username']
    broadcast(sender, f'{username} has logged out')
    data = 'response 22:'
    sender.send(data.encode())
    del settings.online_users[sender]

commands = {
    'broadcast': broadcast,
    'whoelse': whoelse,
    'logout': logout
}