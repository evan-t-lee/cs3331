def username(socket, receiver):
    while True:
        username = input("Username: ")

        socket.sendto(username.encode(), receiver)
        # wait for the reply from the server
        data, serverAddress = socket.recvfrom(2048)
        data = data.decode()
        if data == 'status: valid username':
            return True

        print(data)

def password(socket, receiver):
    while True:
        username = input("Password: ")

        socket.sendto(username.encode(), receiver)
        # wait for the reply from the server
        data, serverAddress = socket.recvfrom(2048)
        data = data.decode()
        
        if data == 'status: authentication granted':
            return True

        print(data, data == 'Invalid Password. Your account has been blocked. Please try again later')

        if data == 'Invalid Password. Your account has been blocked. Please try again later':
            print('hi')
            return False
