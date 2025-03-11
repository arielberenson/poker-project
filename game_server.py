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
        process_data_thread = threading.Thread(target=self.process_data, daemon=True)
        process_data_thread.start()

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

    def send_to_all(self, recipients, m):
        for recipient in recipients:
            try:
                us = recipient.get_user()
                us.get_socket().sendall(m.encode('utf-8'))
            except Exception as e:
                recipient.get_socket().sendall(m.encode('utf-8'))

    def create_message(self, message_type, data1, data2):
        return json.dumps({
            "type": message_type,
            "data1": data1,
            "data2": data2,
        })

    def create_game(self, user):
        p = Player(user, user.get_username(), 1000)
        game_id = f"game_{self.game_counter}"  # Generate game ID like 'game_1', 'game_2', etc.
        new_game = Game(game_id, p)
        self.games[game_id] = new_game
        self.game_counter += 1  # Increment the counter for the next game
        print(f"Game {game_id} created.")


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

    def process_data(self):
        print('process started')
        while True:
            try:
                incoming_message, current_game = self.message_queue.get_nowait()  # Non-blocking get from the queue
                print("RAW message: ", incoming_message)
                extra, incoming_message = self.extract_json(incoming_message)
                print("extra", extra)
                if extra:
                    self.message_queue.put(extra)
                message_data = json.loads(incoming_message)
                message_type = message_data.get("type")
                print("JSON message: ", message_data)
                data1 = message_data.get("data1")
                data2 = message_data.get("data2")

                if message_type == 'create':
                    for user in self.users.get_users():
                        print('username: ', user.get_username())
                        if user.get_username() == data1:
                            self.create_game(user)
                            message = self.create_message('approve', 'create', '')
                            user.get_socket().sendall(message.encode('utf-8'))
                            message = self.create_message('new_game', user.get_username(), '')
                            self.send_to_all(self.users.get_users(), message)

                if message_type == 'join':
                    for user in self.users.get_users():
                        if user.get_username() == data1:
                            message = self.create_message('player-joined', 'lobby', data1)
                            self.send_to_all(current_game.get_players(), message)
                            p = Player(user, user.get_username(), 1000)
                            players.add_players(p)
                            names = []
                            for p in players.get_players():
                                names.append(p.get_username())
                            message = self.create_message('approve', 'join', names)
                            user.get_socket().sendall(message.encode('utf-8'))

                if message_type == 'game-start':
                    game_start = True
                    message = self.create_message('approve', 'game-start', '')
                    self.send_to_all(players.get_players(), message)
                    self.game_queue.put(players)

                if message_type == 'name':
                    for u in self.users.get_users():
                        print("real", u.get_address())
                        print("sent", data2)
                        if u.get_address() == tuple(data2):
                            u.set_username(data1)
                            print('for ', data2, ' accepted ', data1)

                if message_type == 'player_move':
                    if data1 == 'call':
                        print("players last bet: ", players.get_last_bet())
                        place_bet(players, pot, players.get_last_bet())
                        message = self.create_message('player chips', players.get_current().get_name(),
                                                 players.get_current().get_chips())
                        self.send_to_all(players.get_players(), message)
                        message = self.create_message('pot', pot.get_chips(), '')
                        self.send_to_all(players.get_players(), message)
                    elif data1 == 'raise':
                        place_bet(players, pot, data2)
                        message = self.create_message('player chips', players.get_current().get_name(),
                                                 players.get_current().get_chips())
                        self.send_to_all(players.get_players(), message)
                        message = self.create_message('pot', pot.get_chips(), '')
                        self.send_to_all(players.get_players(), message)
                        players.player_raised()
                    elif data1 == 'fold':
                        fold(players)
                    players.next_player()
                    print("Turn count: ", players.get_turn_counter())
                    print("Max Turns: ", players.get_max_turns())
                    game_queue.put((data1, data2))

            except queue.Empty:
                pass  # No message to process, simply skip

            except Exception as e:
                print(f"An error occurred: {e}")


