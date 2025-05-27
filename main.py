from database.firebase import initialize_firebase
from server.server import *

if __name__ == "__main__":
    initialize_firebase()
    server = Server()
