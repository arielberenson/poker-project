import queue
import threading
import select
import socket
from poker_classes import *
import time
import json
from bet import *


class GameServer:
    def __init__(self):
        self.games = {}
        self.game_counter = 1  # To auto-increment the game ID
        self.message_queue = queue.Queue()
        self.admin, self.server_socket = self.start_server()
        self.users = Users([self.admin])
        connect_user_thread = threading.Thread(target=self.add_user, args=(self.server_socket,), daemon=True)
        connect_user_thread.start()
        data_thread = threading.Thread(target=self.recv_data, daemon=True)
        data_thread.start()


    def extract_json(self, data):
        """Extract a complete JSON object from the data, handling nested structures."""
        # Use a stack to track the opening and closing braces
        stack = 0
        start_idx = 0
        for i, char in enumerate(data):
            if char == '{':  # Opening brace
                if stack == 0:
                    start_idx = i
                stack += 1
            elif char == '}':  # Closing brace
                stack -= 1
                if stack == 0:  # Found a complete JSON object
                    return data[i + 1:], data[start_idx:i + 1]  # Return the remaining data and the JSON object
        return data, ""  # If no complete JSON is found, return the data unprocessed



    def create_game(self, user):
        p = Player(user, user.get_username(), 1000)
        game_id = f"game_{self.game_counter}"  # Generate game ID like 'game_1', 'game_2', etc.
        new_game = Game(game_id, p)
        self.games[game_id] = new_game
        self.game_counter += 1  # Increment the counter for the next game
        print(f"Game {game_id} created.")
        new_game_thread = threading.Thread(target=self.run_game, args=(game_id,), daemon=True)
        new_game_thread.start()

    def run_game(self, game_id):
        self.games[game_id].start_game()


    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 8820))  # Bind to all interfaces on port 8820
        server_socket.listen(1)  # Listen for exactly 1 clients (max 1 clients in the queue)
        print("Server is listening for connections...")

        # Accept first client connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from client 1 at {client_address}")
        user = User(client_socket, client_address)
        return user, server_socket

    def add_user(self, server_socket):
        while True:
            server_socket.listen(1)
            print("Server is listening for connections...")

            # Accept first client connection
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from new client at {client_address}")

            user = User(client_socket, client_address)
            self.users.add_user(user)

    def recv_data(self):
        print("Data thread started")  # Debugging message
        while True:
            for user in self.users.get_users():
                readable, _, _ = select.select([user.get_socket()], [], [], 0.1)
                if readable:
                    message = user.get_socket().recv(1024).decode('utf-8')
                    if message:
                        print(message)
                        for game in self.games:
                            for player in game.get_players():
                                if player.get_username() == user.get_username():
                                    current_game = game.get_game_id()
                                    break
                        self.message_queue.put(message, current_game)
                time.sleep(0.1)





