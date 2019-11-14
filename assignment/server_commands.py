import settings

def toggle_blacklist(username):
    settings.users[username]['blacklisted'] = not settings.users[username]['blacklisted']

def broadcast(sender, message):
    data = f'status 10:[broadcast] {message}'
    for username in settings.online_users:
        if sender not in settings.users[username]['blocked_users']:
            settings.online_users[username]['conn'].send(data.encode())
