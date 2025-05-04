from firebase import add_to_db, check_username, check_user_credentials, fetch_data
from game import *


class Server:
    def __init__(self):
        self.games = {}
        self.game_counter = 1  # To auto-increment the game ID
        print("before")
        self.admin, self.server_socket = self.start_server()
        print("after")
        self.users = [self.admin]

        connect_user_thread = threading.Thread(target=self.add_user, args=(self.server_socket,), daemon=True)
        connect_user_thread.start()
        self.recv_data()
        # data_thread = threading.Thread(target=self.recv_data, daemon=True)
        # data_thread.start()

    def create_game(self, user):
        p = Player(user, user.get_username(), 1000)
        game_id = f"game_{self.game_counter}"  # Generate game ID like 'game_1', 'game_2', etc.
        server_to_game_queue = queue.Queue()
        game_to_server_queue = queue.Queue()
        new_game = Game(game_id, [p], server_to_game_queue, game_to_server_queue)
        self.games[game_id] = new_game, server_to_game_queue, game_to_server_queue, p.get_name()
        self.game_counter += 1  # Increment the counter for the next game
        print(f"Game {game_id} created.")
        new_game.create_game()
        return game_id

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 8820))
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
            self.users.append(user)

    def recv_data(self):
        print("Data thread started")  # Debugging message
        while True:
            for user in self.users:
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
                            if len(current_game.get_players()) > 2:
                                message = create_message('reject', 'join', '')
                                user.get_socket().sendall(message.encode('utf-8'))
                            else:
                                p = Player(user, user.get_username(), 1000)
                                if current_game.is_game_started():
                                    current_game.add_pending_players(p)
                                else:
                                    current_game.add_players(p)
                                message = create_message('player_joined', 'lobby', user.get_username())
                                send_to_all(current_game.get_players(), message)
                                names = []
                                for p in current_game.get_players():
                                    names.append(p.get_username())
                                message = create_message('approve', 'join', names)
                                user.get_socket().sendall(message.encode('utf-8'))
                        elif message_type == 'create':
                            game_id = self.create_game(user)
                            message = create_message('approve', 'create', '')
                            user.get_socket().sendall(message.encode('utf-8'))
                            message = create_message('new_game', user.get_username(), game_id)
                            send_to_all(self.users, message)
                        elif message_type == 'sign_up':
                            if check_username(data1):
                                add_to_db(data1, data2)
                                user.add_user_credentials(data1, fetch_data(data1, 'chips'))
                                for game_id, game_data in self.games.items():
                                    message = create_message('new_game', game_data[3], game_id)
                                    user.get_socket().sendall(message.encode('utf-8'))
                                message = create_message('approve', 'user', (data1, user.get_chips()))
                            else:
                                message = create_message('reject', 'user', '')
                            user.get_socket().sendall(message.encode('utf-8'))
                        elif message_type == 'log_in':
                            if check_user_credentials(data1, data2) and self.check_username(data1):
                                user.add_user_credentials(data1, fetch_data(data1, 'chips'))
                                for game_id, game_data in self.games.items():
                                    message = create_message('new_game', game_data[3], game_id)
                                    user.get_socket().sendall(message.encode('utf-8'))
                                message = create_message('approve', 'log in', (data1, user.get_chips()))
                            else:
                                message = create_message('reject', 'log in', data1)
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
            remove_games = []
            for game_id, game_data in self.games.items():
                try:
                    incoming_message = game_data[2].get_nowait()
                    print("RAW message: ", incoming_message)
                    extra, incoming_message = extract_json(incoming_message)
                    print("extra", extra)
                    if extra:
                        game_data[2].put(extra)
                    message_data = json.loads(incoming_message)
                    message_type = message_data.get("type")
                    print("JSON message: ", message_data)
                    data1 = message_data.get("data1")
                    data2 = message_data.get("data2")

                    if message_type == 'remove_game':
                        remove_games.append(game_id)
                        message = create_message('remove_game', game_id, '')
                        send_to_all(self.users, message)

                except queue.Empty:
                    pass  # No message to process, simply skip

                except Exception as e:
                    print(f"An error occurred: {e}")

            for game_id in remove_games:
                self.games.pop(game_id, None)

    def check_username(self, username):
        for u in self.users:
            if u.get_username() == username:
                return False
        return True
