from firebase import initialize_firebase
from game_server import *

if __name__ == "__main__":
    initialize_firebase()
    game_server = GameServer()
