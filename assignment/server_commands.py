import settings

def toggle_blacklist(username):
    settings.users[username]['blacklisted'] = not settings.users[username]['blacklisted']

def message():

def broadcast(sender, message):
    data = f'status 10:[broadcast] {message}'
    for username in settings.online_users:
        if sender not in settings.users[username]['blocked_users']:
            settings.online_users[username]['conn'].send(data.encode())


def whoelse(sender):
    users = [user for user in settings.online_users if user != sender]
    print('Online users:' ,', '.join(users))

# def whoelsesince(sender, time_since):
#     curr_time = time.time()
#     for username in settings.online_users:
#         if username != sender:
#             if curr_time - settings.online_users[username]['time_logged_in'] < time_since:
#                 print(username)

# def block():

# def unblock():

def logout(username):
    data = 'status 22:'
    settings.online_users[username]['conn'].send(data.encode())
    del settings.online_users[username]
