import json
import threading
from poker_classes import *
from bet import *
from compute_winner import *
import socket
from queue import Queue
import queue
import time
import select
from game_server import *


def send_to_all(recipients, m):
    for recipient in recipients:
        try:
            us = recipient.get_user()
            us.get_socket().sendall(m.encode('utf-8'))
        except Exception as e:
            recipient.get_socket().sendall(m.encode('utf-8'))


def create_message(message_type, data1, data2):
    return json.dumps({
        "type": message_type,
        "data1": data1,
        "data2": data2,
    })


def extract_json(data):
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


def recv_data():
    print("Data thread started")  # Debugging message
    while True:
        for user in users.get_users():
            readable, _, _ = select.select([user.get_socket()], [], [], 0.1)
            if readable:
                message = user.get_socket().recv(1024).decode('utf-8')
                if message:
                    print(message)
                    message_queue.put(message)
            time.sleep(0.1)


'''
def handle_turn(players, player, round):
    """Handles communication with the client for a single turn."""

        # Receive the client's move
        message = user.get_socket().recv(1024).decode('utf-8')
        message_data = json.loads(message)
        message_data1 = message_data.get("data1")
        message_data2 = message_data.get("data2")

        return message_data1, message_data2


    except Exception as e:
        print(f"Error with client {user.get_address()}: {e}")
        return None
'''


def start_server():
    """Starts the server to handle two clients and manage turns."""
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8820))  # Bind to all interfaces on port 8820
    server_socket.listen(1)  # Listen for exactly 1 clients (max 1 clients in the queue)
    print("Server is listening for connections...")

    # Accept first client connection
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from client 1 at {client_address}")
    user = User(client_socket, client_address)
    return user, server_socket


def add_user(server_socket):
    while True:
        server_socket.listen(1)
        print("Server is listening for connections...")

        # Accept first client connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from new client at {client_address}")

        user = User(client_socket, client_address)
        users.add_user(user)


def process_data():
    print('process started')
    while True:
        try:
            incoming_message = message_queue.get_nowait()  # Non-blocking get from the queue
            print("RAW message: ", incoming_message)
            extra, incoming_message = extract_json(incoming_message)
            print("extra", extra)
            if extra:
                message_queue.put(extra)
            message_data = json.loads(incoming_message)
            message_type = message_data.get("type")
            print("JSON message: ", message_data)
            data1 = message_data.get("data1")
            data2 = message_data.get("data2")

            if message_type == 'create':
                for user in users.get_users():
                    print('username: ', user.get_username())
                    if user.get_username() == data1:
                        p = Player(user, user.get_username(), 1000)
                        players = Game([p])
                        message = create_message('approve', 'create', '')
                        user.get_socket().sendall(message.encode('utf-8'))
                        message = create_message('new_game', user.get_username(), '')
                        send_to_all(users.get_users(), message)

            if message_type == 'join':
                for user in users.get_users():
                    if user.get_username() == data1:
                        message = create_message('player-joined', 'lobby', data1)
                        send_to_all(players.get_players(), message)
                        p = Player(user, user.get_username(), 1000)
                        players.add_players(p)
                        names = []
                        for p in players.get_players():
                            names.append(p.get_username())
                        message = create_message('approve', 'join', names)
                        user.get_socket().sendall(message.encode('utf-8'))

            if message_type == 'game-start':
                game_start = True
                message = create_message('approve', 'game-start', '')
                send_to_all(players.get_players(), message)
                game_queue.put(players)

            if message_type == 'name':
                for u in users.get_users():
                    print("real", u.get_address())
                    print("sent", data2)
                    if u.get_address() == tuple(data2):
                        u.set_username(data1)
                        print('for ', data2, ' accepted ', data1)

            if message_type == 'player_move':
                if data1 == 'call':
                    print("players last bet: ", players.get_last_bet())
                    place_bet(players, pot, players.get_last_bet())
                    message = create_message('player chips', players.get_current().get_name(),
                                             players.get_current().get_chips())
                    send_to_all(players.get_players(), message)
                    message = create_message('pot', pot.get_chips(), '')
                    send_to_all(players.get_players(), message)
                elif data1 == 'raise':
                    place_bet(players, pot, data2)
                    message = create_message('player chips', players.get_current().get_name(),
                                             players.get_current().get_chips())
                    send_to_all(players.get_players(), message)
                    message = create_message('pot', pot.get_chips(), '')
                    send_to_all(players.get_players(), message)
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


def new_round():
    pot.clear_pot()
    deck.create_deck()
    deck.shuffle()
    community.clear(deck)
    for player in players.get_players():
        player.clear()


def run_game(players):
    new_round()
    print("game start")
    for player in players.get_players():
        user = player.get_user()
        message = create_message('new-round', '', '')
        user.get_socket().sendall(message.encode('utf-8'))
        player.get_hand(deck)
        # Convert each card to a dictionary
        cards_dict = [card.to_dict() for card in player.get_cards()]
        message = create_message('player-cards', cards_dict, player.get_chips())
        user.get_socket().sendall(message.encode('utf-8'))

    players_data = []
    for player in players.get_players():
        data = (player.get_username(), player.get_chips())
        players_data.append(data)
    message = create_message('players', players_data, '')
    send_to_all(players.get_players(), message)
    print(players_data)

    round = 0
    while round < 4:
        if len(players.get_players()) == 1:
            break
        round += 1
        print(round)
        players.new_round()
        print("Turn count: ", players.get_turn_counter())
        print("Max Turns: ", players.get_max_turns())
        message = create_message('round_bet', 0, '')
        send_to_all(players.get_players(), message)
        if round == 2:
            print("round 2 entered")
            community.flop()
            cards_dict = [card.to_dict() for card in community.get_cards()]
            message = create_message('round', round, cards_dict)
            print(message)
            send_to_all(players.get_players(), message)
        elif round > 2:
            community.turn()
            c = [community.get_cards()[round]]
            cards_dict = [card.to_dict() for card in c]
            message = create_message('round', round, cards_dict)
            send_to_all(players.get_players(), message)
        while players.get_turn_counter() < players.get_max_turns():
            print(players.get_current().get_username())
            try:
                if players.get_last_bet() > 0:
                    pressure = 'pressure'
                else:
                    pressure = 'no pressure'
                user = players.get_current().get_user()
                # Notify the current player whose turn it is
                message = create_message('turn', players.get_current().get_username(), pressure)
                send_to_all(players.get_players(), message)
            except Exception as e:
                print(f"Error with client {user.get_address()}: {e}")
                return None
            player_moved = game_queue.get()
            if player_moved:
                send_to_all(players.get_players(), create_message('player-moved', players.get_current().get_username(),
                                                                  (player_moved[0], player_moved[0])))

    print("game over")
    winner = compute_winner(players, community)
    print(winner[0].get_username())
    winner[0].add_chips(pot.get_chips())

    run_game(players)


if __name__ == "__main__":
    message_queue = queue.Queue()
    game_queue = queue.Queue()
    admin, server_socket = start_server()
    users = Users([admin])
    connect_user_thread = threading.Thread(target=add_user, args=(server_socket,), daemon=True)
    connect_user_thread.start()
    data_thread = threading.Thread(target=recv_data, daemon=True)
    data_thread.start()
    process_data_thread = threading.Thread(target=process_data, daemon=True)
    process_data_thread.start()
    players = game_queue.get()
    if players:
        small = 5
        big = 10
        pot = Pot()
        deck = Deck()
        deck.shuffle()
        community = Communal(deck)
        run_game(players)
    data_thread.join()
    process_data_thread.join()
