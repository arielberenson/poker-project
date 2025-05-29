import queue
import threading
import socket
import select

from classes.game_classes.deck import *
from classes.game_classes.pot import *
from classes.users_classes.user import *
from classes.users_classes.player import *

from extra_functions import *
from compute_winner import compute_winner
from database.firebase import update_chips


class Game:
    def __init__(self, game_id, players, server_to_game_queue, game_to_server_queue):
        self.pending_players = []
        self.id = game_id
        self.players = players
        self.big = players[0]
        self.current = self.big
        self.last_bet = 0
        self.turn_counter = 0
        self.max_turns = len(self.players)
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = Communal()
        self.server_to_game_queue = server_to_game_queue
        self.game_to_server_queue = game_to_server_queue
        self.game_queue = queue.Queue()
        self.process_data_thread = threading.Thread(target=self.process_data, daemon=True)
        self.run_game_thread = threading.Thread(target=self.start_game, daemon=True)
        self.pots = PotList()
        self.history = []
        self.game_started = False
        self.terminate = False

    def is_game_started(self):
        return self.game_started

    def play_again(self):
        print("PLAY AGAIN")
        if self.pending_players:
            for player in self.pending_players:
                self.players.append(player)
            self.pending_players = []
        self.big = self.players[0]
        self.current = self.big
        self.pots.clear_all()
        self.deck.new_deck()
        self.deck.shuffle()
        self.community_cards.clear()
        for player in self.players:
            player.new_game()
        self.turn_counter = 0
        self.max_turns = len(self.players)

    def everyone_folded(self):
        count = 0
        for player in self.players:
            if player.is_active():
                count += 1
        if count <= 1:
            return True
        else:
            return False

    def new_round(self):
        for player in self.players:
            player.new_round()
        self.last_bet = 0
        self.turn_counter = 0
        self.current = self.big
        while self.players[0] != self.big:
            self.players.append(self.players.pop(0))
        self.max_turns = len(self.players)

    def create_game(self):
        self.process_data_thread.start()

    def start_game(self):
        while True and not self.terminate:
            print('gaming')
            play_again = self.game_queue.get()
            if play_again == 'play_again' and not self.terminate:
                self.play_again()
                print("game start")
                for player in self.players:
                    user = player.get_user()
                    message = create_message('play_again', '', '')
                    user.get_socket().sendall(message.encode('utf-8'))
                    player.get_hand(self.deck)
                    # Convert each card to a dictionary
                    cards_dict = [card.to_dict() for card in player.get_cards()]
                    message = create_message('player_cards', cards_dict, player.get_chips())
                    user.get_socket().sendall(message.encode('utf-8'))

                players_data = []
                for player in self.players:
                    data = (player.get_username(), player.get_chips())
                    players_data.append(data)
                message = create_message('players', players_data, '')
                send_to_all(self.players, message)
                print(players_data)
                still_playing = True

                round = 0
                while round < 4 and still_playing and not self.terminate:
                    # still playing: if everyone folded, terminate: if everyone left the game
                    round += 1
                    print(round)
                    self.new_round()
                    print("Turn count: ", self.turn_counter)
                    print("Max Turns: ", self.max_turns)
                    message = create_message('round_bet', 0, '')
                    send_to_all(self.players, message)
                    if round == 1:
                        self.last_bet = 5
                    if round == 2:
                        print("round 2 entered")
                        for i in range(3):
                            self.community_cards.add_card(self.deck.take_card())
                        cards_dict = [card.to_dict() for card in self.community_cards.get_cards()]
                        message = create_message('round', round, cards_dict)
                        print(message)
                        send_to_all(self.players, message)
                    elif round > 2:
                        self.community_cards.add_card(self.deck.take_card())
                        c = [self.community_cards.get_cards()[round]]
                        cards_dict = [card.to_dict() for card in c]
                        message = create_message('round', round, cards_dict)
                        send_to_all(self.players, message)
                    while self.turn_counter < self.max_turns and not self.terminate and still_playing:
                        print(self.current.get_username())
                        try:
                            user = self.current.get_user()
                            # Notify the current player whose turn it is
                            message = create_message('turn', self.current.get_username(), self.last_bet)
                            send_to_all(self.players, message)
                        except Exception as e:
                            print(f"Error with client {user.get_address()}: {e}")
                            return None
                        if self.everyone_folded():
                            still_playing = False
                            break
                        player_moved = self.game_queue.get()
                        if player_moved and not self.terminate:
                            message = create_message('player_moved', self.current.get_username(), player_moved)
                            send_to_all(self.players, message)

                self.new_round()
                print("game over")
                winners = compute_winner(self.players, self.community_cards)
                winners_names = []
                for player in winners:
                    player.add_chips(int(self.pots.get_chips()/len(winners)))
                    winners_names.append(player.get_name())
                print(winners[0].get_username())

                players_data = []
                for player in self.players:
                    cards_dict = [card.to_dict() for card in player.get_cards()]
                    data = (player.get_username(), cards_dict)
                    players_data.append(data)

                message = create_message('game_over', winners_names, players_data)
                send_to_all(self.players, message)

                for player in self.players:
                    print("before update chips")
                    update_chips(player.get_username(), player.get_chips())
                self.game_queue.put('waiting')

    def process_data(self):
        print('process started')
        while True:
            try:
                incoming_message = self.server_to_game_queue.get_nowait()  # Non-blocking get from the queue
                print("RAW message: ", incoming_message)
                extra, incoming_message = extract_json(incoming_message)
                print("extra", extra)
                if extra:
                    self.server_to_game_queue.put(extra)
                message_data = json.loads(incoming_message)
                message_type = message_data.get("type")
                print("JSON message: ", message_data)
                data1 = message_data.get("data1")
                data2 = message_data.get("data2")

                if message_type == 'start_game':
                    self.game_started = True
                    message = create_message('approve', 'start_game', '')
                    send_to_all(self.players, message)
                    self.run_game_thread.start()
                    self.game_queue.put('play_again')

                elif message_type == 'leave_game':
                    for player in self.players:
                        if player.get_username() == data1:
                            self.players.remove(player)
                    if len(self.players) == 0:
                        message = create_message('remove_game', '', '')
                        self.game_to_server_queue.put(message)
                        self.terminate = True
                        break
                    else:
                        message = create_message('player_left', data1, '')
                        send_to_all(self.players, message)
                        if data2:
                            message = create_message('game_host', '', '')
                            self.players[0].get_user().get_socket().sendall(message.encode('utf-8'))

                elif message_type == 'play_again':
                    self.game_queue.put('play_again')

                elif message_type == 'player_move':
                    if data1 == 'call':
                        print("players last bet: ", self.last_bet)
                        self.place_bet(self.last_bet)
                        message = create_message('player chips', self.current.get_name(),
                                                 self.current.get_chips())
                        send_to_all(self.players, message)
                        message = create_message('pot', self.pots.get_chips(), '')
                        send_to_all(self.players, message)
                    elif data1 == 'raise':
                        self.place_bet(data2)
                        message = create_message('player chips', self.current.get_name(),
                                                 self.current.get_chips())
                        send_to_all(self.players, message)
                        message = create_message('pot', self.pots.get_chips(), '')
                        send_to_all(self.players, message)
                        self.player_raised()
                    elif data1 == 'fold':
                        self.current.set_active(False)
                    self.next_player()
                    print("Turn count: ", self.turn_counter)
                    print("Max Turns: ", self.max_turns)
                    self.game_queue.put((data1, data2))

            except queue.Empty:
                pass  # No message to process, simply skip

            except Exception as e:
                print(f"An error occurred: {e}")

    def player_raised(self):
        self.max_turns += self.turn_counter

    def next_player(self):
        first = True
        while self.current.is_allin() or first:
            self.players.append(self.players.pop(0))  # Move the first player to the end of the list
            self.current = self.players[0]
            first = False
        self.turn_counter += 1

    def place_bet(self, n):
        if n >= self.current.get_chips():
            old, new = self.pots.side_pot(self.current, self.current.get_chips(), n)
            self.current.remove_chips(self.current.get_chips())
            message = create_message('new_pot', old.get_chips(), new.get_chips())
            send_to_all(self.players, message)
            self.current.set_allin(True)
        else:
            self.current.remove_chips(n)
            self.pots.add_action(self.current, n)
        if self.last_bet < n:
            self.last_bet = n

    def add_players(self, p):
        self.players.append(p)

    def add_pending_players(self, p):
        self.pending_players.append(p)

    def get_players(self):
        return self.players
