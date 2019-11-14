def username(socket, receiver):
    while True:
        username = input("> Username: ")

        socket.sendto(username.encode(), receiver)
        # wait for the reply from the server
        data, address = socket.recvfrom(2048)
        data = data.decode()
        status, message = data.split(':')
        if status == 'status 10':
            return True

        print(message)

        if status == 'status 30':
            return False

def password(socket, receiver):
    while True:
        username = input("> Password: ")

        socket.sendto(username.encode(), receiver)
        # wait for the reply from the server
        data, address = socket.recvfrom(2048)
        data = data.decode()
        status, message = data.split(':')
        if status == 'status 11':
            return True

        print(message)

        if status == 'status 30':
            return False
