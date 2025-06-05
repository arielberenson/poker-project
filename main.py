from database.firebase_shared import initialize_firebase
from database.firebase_server import update_server_ip
from server.server import *


if __name__ == "__main__":
    initialize_firebase()
    update_server_ip()
    server = Server()
