import random
import queue
import threading
import select
import socket
import time
import json

from extra_functions import *
from bet import place_bet, fold
from compute_winner import compute_winner


# https://cardscans.piwigo.com/index?/category/706-g
# https://nicubunu.ro/graphics:playingcards


class Game:
    def __init__(self, game_id, players, message_queue):
        self.id = game_id
        self.players = players
        self.current = players[0]
        self.big = players[0]
        self.last_bet = 0
        self.turn_counter = 0
        self.max_turns = len(self.players)
        self.deck = Deck()
        self.community_cards = Communal(self.deck)
        self.message_queue = message_queue
        self.game_queue = queue.Queue()
        self.pot = Pot()

    def new_round(self):
        self.pot.clear_pot()
        self.deck.create_deck()
        self.deck.shuffle()
        self.community_cards.clear(self.deck)
        for player in self.get_players():
            player.clear()

    def start_game(self):
        process_data_thread = threading.Thread(target=self.process_data, daemon=True)
        process_data_thread.start()
        self.new_round()
        print("game start")
        for player in self.get_players():
            user = player.get_user()
            message = create_message('new-round', '', '')
            user.get_socket().sendall(message.encode('utf-8'))
            player.get_hand(self.deck)
            # Convert each card to a dictionary
            cards_dict = [card.to_dict() for card in player.get_cards()]
            message = create_message('player-cards', cards_dict, player.get_chips())
            user.get_socket().sendall(message.encode('utf-8'))

        players_data = []
        for player in self.get_players():
            data = (player.get_username(), player.get_chips())
            players_data.append(data)
        message = create_message('players', players_data, '')
        send_to_all(self.players, message)
        print(players_data)

        round = 0
        while round < 4:
            if len(self.players) == 1:
                break
            round += 1
            print(round)
            self.new_round()
            print("Turn count: ", self.get_turn_counter())
            print("Max Turns: ", self.get_max_turns())
            message = create_message('round_bet', 0, '')
            send_to_all(self.players, message)
            if round == 2:
                print("round 2 entered")
                self.community_cards.flop()
                cards_dict = [card.to_dict() for card in self.community_cards.get_cards()]
                message = create_message('round', round, cards_dict)
                print(message)
                send_to_all(self.players, message)
            elif round > 2:
                self.community_cards.turn()
                c = [self.community_cards.get_cards()[round]]
                cards_dict = [card.to_dict() for card in c]
                message = create_message('round', round, cards_dict)
                send_to_all(self.players, message)
            while self.get_turn_counter() < self.get_max_turns():
                print(self.get_current().get_username())
                try:
                    if self.get_last_bet() > 0:
                        pressure = 'pressure'
                    else:
                        pressure = 'no pressure'
                    user = self.get_current().get_user()
                    # Notify the current player whose turn it is
                    message = create_message('turn', self.get_current().get_username(), pressure)
                    send_to_all(self.players, message)
                except Exception as e:
                    print(f"Error with client {user.get_address()}: {e}")
                    return None
                player_moved = self.game_queue.get()
                if player_moved:
                    message = create_message('player-moved', self.get_current().get_username(), player_moved)
                    send_to_all(self.players, message)

        print("game over")
        winner = compute_winner(self.players, self.community_cards)
        print(winner[0].get_username())
        winner[0].add_chips(self.pot.get_chips())

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

                if message_type == 'game-start':
                    game_start = True
                    message = create_message('approve', 'game-start', '')
                    send_to_all(current_game.get_players(), message)
                    self.game_queue.put(current_game)

                if message_type == 'player_move':
                    if data1 == 'call':
                        print("players last bet: ", current_game.get_last_bet())
                        place_bet(current_game, self.pot, current_game.get_last_bet())
                        message = create_message('player chips', current_game.get_current().get_name(),
                                                      current_game.get_current().get_chips())
                        send_to_all(current_game.get_players(), message)
                        message = create_message('pot', self.pot.get_chips(), '')
                        send_to_all(current_game.get_players(), message)
                    elif data1 == 'raise':
                        place_bet(current_game, self.pot, data2)
                        message = create_message('player chips', current_game.get_current().get_name(),
                                                      current_game.get_current().get_chips())
                        send_to_all(current_game.get_players(), message)
                        message = create_message('pot', self.pot.get_chips(), '')
                        send_to_all(current_game.get_players(), message)
                        current_game.player_raised()
                    elif data1 == 'fold':
                        fold(current_game)
                    current_game.next_player()
                    print("Turn count: ", current_game.get_turn_counter())
                    print("Max Turns: ", current_game.get_max_turns())
                    self.game_queue.put((data1, data2))

            except queue.Empty:
                pass  # No message to process, simply skip

            except Exception as e:
                print(f"An error occurred: {e}")

    def player_raised(self):
        self.max_turns += self.turn_counter

    def next_player(self):
        self.players.append(self.players.pop(0))  # Move the first player to the end of the list
        self.current = self.players[0]
        self.turn_counter += 1

    def new_round(self):
        while self.players[0] != self.big:
            self.players.append(self.players.pop(0))
        for p in self.players:
            p.set_round_bet(0)
        self.current = self.players[0]
        self.turn_counter = 0
        self.max_turns = len(self.players)
        self.last_bet = 0

    def set_last_bet(self, bet):
        self.last_bet = bet

    def get_last_bet(self):
        return self.last_bet

    def remove_first_player(self):
        self.players.pop(0)
        self.current = self.players[0]

    def get_current(self):
        return self.current

    def get_players(self):
        return self.players

    def get_turn_counter(self):
        return self.turn_counter

    def get_max_turns(self):
        return self.max_turns

    def add_players(self, p):
        self.players.append(p)


class User:
    def __init__(self, client_socket, client_address, username=None, password=None):
        self.username = username
        self.password = password
        self.socket = client_socket
        self.address = client_address

    def get_socket(self):
        return self.socket

    def get_address(self):
        return self.address

    def get_username(self):
        return self.username

    def create_account(self, username, password):
        self.username = username
        self.password = password


class Users:
    def __init__(self, users):
        self.users = users

    def add_user(self, user):
        self.users.append(user)

    def find_user(self, username):
        user = next((u for u in self.users if u.get_username() == username), None)
        return user

    def get_users(self):
        return self.users


class Player:
    def __init__(self, user, username, chips):
        self.user = user
        self.cards = []
        self.username = username
        self.chips = chips
        self.round_bet = 0

    def remove_chips(self, n):
        self.chips -= int(n)
        self.round_bet += int(n)

    def add_chips(self, n):
        self.chips += n

    def new_round(self):
        self.round_bet = 0

    def get_name(self):
        return self.username

    def get_hand(self, deck):
        for i in range(2):
            self.cards.append(deck.take_card())

    def get_chips(self):
        return self.chips

    def get_cards(self):
        return self.cards

    def set_cards(self, card1, card2):
        self.cards = []
        self.cards.append(card1)
        self.cards.append(card2)

    def get_user(self):
        return self.user

    def get_username(self):
        return self.username

    def get_round_bet(self):
        return self.round_bet

    def set_round_bet(self, n):
        self.round_bet = n

    def clear(self):
        self.cards = []


class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val
        self.img = 'white/white_{}_{}.svg'.format(suit.lower(), val)

    def get_suit(self):
        return self.suit

    def get_val(self):
        return self.val

    def get_img(self):
        return self.img

    # Convert the object into a dictionary to make it JSON serializable
    def to_dict(self):
        return {
            'suit': self.suit,
            'val': self.val,
            'img': self.img,
        }


class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()

    def create_deck(self):
        vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        suits = ['H', 'D', 'C', 'S']
        self.cards = [Card(suit, val) for suit in suits for val in vals]

    def shuffle(self):
        random.shuffle(self.cards)

    def take_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None

    def get_cards(self):
        return self.cards


class Pot:
    def __init__(self):
        self.chips = 0

    def add_chips(self, n):
        self.chips += n

    def clear_pot(self):
        self.chips = 0

    def get_chips(self):
        return self.chips


class Communal:
    def __init__(self, deck):
        self.cards = []
        self.deck = deck

    def flop(self):
        for i in range(3):
            self.cards.append(self.deck.take_card())

    def turn(self):
        self.cards.append(self.deck.take_card())

    def river(self):
        self.cards.append(self.deck.take_card())

    def get_cards(self):
        return self.cards

    def clear(self, deck):
        self.cards = []
        self.deck = deck
