def username(socket):
    while True:
        username = input("Username: ")
        data = f"request 10:{username}"
        socket.send(data.encode())

        # wait for the reply from the server
        data = socket.recv(2048).decode()
        code, message = data.split(':')
        if code == 'response 20':
            return username

        print(message)

        if code == 'response 40':
            return False

def password(socket):
    while True:
        password = input("Password: ")
        data = f"request 11:{password}"
        socket.send(data.encode())

        # wait for the reply from the server
        data = socket.recv(2048).decode()
        code, response = data.split(':')
        if code == 'response 21':
            return True

        print(response)

        if code == 'response 40':
            return False
