from firebase import initialize_firebase
from server import *

if __name__ == "__main__":
    initialize_firebase()
    server = Server()
