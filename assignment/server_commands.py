import settings

def block_user_login(username):
    settings.blocked_users.append(username)

def unblock_user_login(username):
    settings.blocked_users.remove(username)

def broadcast(message):
    