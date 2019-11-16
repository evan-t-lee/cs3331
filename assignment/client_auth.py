def username(socket):
    while True:
        username = input("Username: ")

        socket.send(username.encode())
        # wait for the reply from the server
        data, address = socket.recvfrom(2048)
        data = data.decode()
        status, message = data.split(':')
        if status == 'status 20':
            return True

        print(message)

        if status == 'status 40':
            return False

def password(socket):
    while True:
        username = input("Password: ")

        socket.send(username.encode())
        # wait for the reply from the server
        data, address = socket.recvfrom(2048)
        data = data.decode()
        status, message = data.split(':')
        if status == 'status 21':
            return True

        print(message)

        if status == 'status 40':
            return False
