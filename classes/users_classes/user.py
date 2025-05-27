class User:
    def __init__(self, client_socket, client_address, username=None, chips=None):
        self.username = username
        self.socket = client_socket
        self.address = client_address
        self.chips = chips

    def get_socket(self):
        return self.socket

    def get_chips(self):
        return self.chips

    def get_address(self):
        return self.address

    def get_username(self):
        return self.username

    def add_user_credentials(self, username, chips):
        self.username = username
        self.chips = chips