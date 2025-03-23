import queue
import threading
import select
import socket

from firebase import add_to_db, check_username, check_user_credentials
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

    def create_game(self, user):
        p = Player(user, user.get_username(), 1000)
        game_id = f"game_{self.game_counter}"  # Generate game ID like 'game_1', 'game_2', etc.
        message_queue = queue.Queue()
        new_game = Game(game_id, [p], message_queue)
        self.games[game_id] = new_game, message_queue
        self.game_counter += 1  # Increment the counter for the next game
        print(f"Game {game_id} created.")
        new_game.create_game()
        return game_id

    def run_game(self, game_id):
        self.games[game_id][0].start_game()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0' , 8820))
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
                        if message_type == 'join':
                            for game_id, game_data in self.games.items():
                                if game_id == data1:
                                    current_game = game_data[0]
                                    break
                            message = create_message('player-joined', 'lobby', data1)
                            send_to_all(current_game.get_players(), message)
                            p = Player(user, user.get_username(), 1000)
                            current_game.add_players(p)
                            names = []
                            for p in current_game.get_players():
                                names.append(p.get_username())
                            message = create_message('approve', 'join', names)
                            user.get_socket().sendall(message.encode('utf-8'))
                        elif message_type == 'create':
                            print('username: ', user.get_username())
                            game_id = self.create_game(user)
                            message = create_message('approve', 'create', '')
                            user.get_socket().sendall(message.encode('utf-8'))
                            message = create_message('new_game', user.get_username(), game_id)
                            send_to_all(self.users.get_users(), message)
                        elif message_type == 'sign_up':
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
                        elif message_type == 'log_in':
                            if user.get_address() == tuple(data2):
                                if check_user_credentials(data1):
                                    user.create_account(data1[0], data1[1])
                                    message = create_message('approve', 'log in', data1[0])
                                else:
                                    message = create_message('reject', 'log in', data1[0])
                                user.get_socket().sendall(message.encode('utf-8'))
                        else:
                            print(self.games)
                            for game in self.games.values():
                                print(game)
                                print(game[0].get_players())
                                for player in game[0].get_players():
                                    if player.get_username() == user.get_username():
                                        current_game = game
                                        break
                            current_game[1].put(message)