def username(socket, port):
    while True:
        username = input("Username: ")
        data = f"request 10:{port}:{username}"
        socket.send(data.encode())

        # confirm whether valid username
        data = socket.recv(2048).decode()
        code, message = data.split(':')
        if code == 'response 20':
            return username

        print(message)

        if code == 'response 40':
            return False

def password(socket, port):
    while True:
        password = input("Password: ")
        data = f"request 11:{port}:{password}"
        socket.send(data.encode())

        # confirm whether authenticated
        data = socket.recv(2048).decode()
        code, response = data.split(':')

        # authenticated
        if code == 'response 21':
            return True

        print(response)

        # blocked
        if code == 'response 40':
            return False
