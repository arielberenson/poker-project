import queue
import threading
import select
import socket

from firebase import add_to_db, check_username
from poker_classes import *
import time
import json
from bet import *


class GameServer:
    def __init__(self):
        self.games = {}
        self.game_counter = 1  # To auto-increment the game ID
        self.message_queue = queue.Queue()
        print("before")
        self.admin, self.server_socket = self.start_server()
        print("after")
        self.users = Users([self.admin])

        connect_user_thread = threading.Thread(target=self.add_user, args=(self.server_socket,), daemon=True)
        connect_user_thread.start()
        self.recv_data()
        # data_thread = threading.Thread(target=self.recv_data, daemon=True)
        # data_thread.start()


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
        message_queue = queue.Queue()
        new_game = Game(game_id, [p], message_queue)
        self.games[game_id] = new_game, message_queue
        self.game_counter += 1  # Increment the counter for the next game
        print(f"Game {game_id} created.")
        new_game_thread = threading.Thread(target=self.run_game, args=(game_id,), daemon=True)
        new_game_thread.start()

    def run_game(self, game_id):
        self.games[game_id][0].start_game()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1' , 8820))
        server_socket.listen(1)
        print("Server is listening for connections...")
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

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
                        message_data = json.loads(message)
                        message_type = message_data.get("type")
                        print("JSON message: ", message_data)
                        data1 = message_data.get("data1")
                        data2 = message_data.get("data2")

                        if message_type == 'create':
                            for user in self.users.get_users():
                                print('username: ', user.get_username())
                                if user.get_username() == data1:
                                    self.create_game(user)
                                    message = create_message('approve', 'create', '')
                                    user.get_socket().sendall(message.encode('utf-8'))
                                    message = create_message('new_game', user.get_username(), '')
                                    send_to_all(self.users.get_users(), message)

                        elif message_type == 'join':
                            for user in self.users.get_users():
                                if user.get_username() == data1:
                                    message = create_message('player-joined', 'lobby', data1)
                                    send_to_all(current_game.get_players(), message)
                                    p = Player(user, user.get_username(), 1000)
                                    current_game.add_players(p)
                                    names = []
                                    for p in current_game.get_players():
                                        names.append(p.get_username())
                                    message = create_message('approve', 'join', names)
                                    user.get_socket().sendall(message.encode('utf-8'))
                        elif message_type == 'sign_up':
                            for user in self.users.get_users():
                                print("real", user.get_address())
                                print("sent", data2)
                                if user.get_address() == tuple(data2):
                                    if check_username(data1[0]):
                                        add_to_db(data1)
                                        user.create_account(data1[0], data1[1])
                                        print('for ', data2, ' accepted ', data1[0])
                                        message = create_message('approve', 'user', data1[0])
                                    else:
                                        message = create_message('reject', 'user', '')
                                    user.get_socket().sendall(message.encode('utf-8'))
                        else:
                            print(self.games)
                            for game in self.games.values():
                                print(game)
                                for player in game[0].get_players():
                                    if player.get_username() == user.get_username():
                                        current_game = game
                                        break
                            current_game[1].put(message)
