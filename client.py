import pygame
import threading
import time
import socket
import json
from queue import Queue
from poker_classes import Card
from pygame_classes import *
import select
import queue


def create_message(message_type, data1, data2):
    return json.dumps({
        "type": message_type,
        "data1": data1,
        "data2": data2,
    })


class Game:
    def __init__(self):
        # Initialize key game variables
        self.submit_sign_up_button = None
        self.sign_up_username = None
        self.sign_up_password = None
        self.name = None
        self.whose_turn = None
        self.screen = None
        self.chips = None
        self.pot = 0
        self.check_call_button = None
        self.raise_button = None
        self.fold_button = None
        self.pot_display = None
        self.input_field = None
        self.community_card_1 = None
        self.community_card_2 = None
        self.community_card_3 = None
        self.community_card_4 = None
        self.community_card_5 = None
        self.players_display = None
        self.confirm_button = None
        self.me_display = None
        self.my_socket = None
        self.update_queue = Queue()
        self.cards = []
        self.last_bet = 0
        self.running = True
        self.SH = None
        self.SW = None
        self.players_data = None
        self.join_button_list = None
        self.create_button = None
        self.start_button = None
        self.players_lobby_display = None
        self.log_in_button = None
        self.sign_up_button = None

    def init_pygame(self):
        pygame.init()

        screen_info = pygame.display.Info()
        self.SW = screen_info.current_w  # Width of the screen
        self.SH = screen_info.current_h * 0.9  # Height of the screen

        self.screen = pygame.display.set_mode((self.SW, self.SH))
        pygame.display.set_caption('Poker Game')

        # Create buttons and displays
        self.join_button_list = GamesDisplay()
        self.submit_sign_up_button = Button(200, 100, "Submit", self.SW * 0.4, self.SH * 0.8)
        self.sign_up_username = TextInput(self.SW * 0.4, self.SH * 0.2, 200, 100)
        self.sign_up_password = TextInput(self.SW * 0.4, self.SH * 0.4, 200, 100)
        self.create_button = Button(200, 200, "Create", self.SW * 0.60, self.SH * 0.3)
        self.check_call_button = Button(100, 50, "Check", self.SW * 0.35, self.SH * 0.875)
        self.raise_button = Button(100, 50, "Raise", self.SW * 0.45, self.SH * 0.875)
        self.fold_button = Button(100, 50, "Fold", self.SW * 0.55, self.SH * 0.875)
        self.pot_display = TextDisplay(20, 300, 36, (0, 0, 0), "[Pot]")
        self.input_field = TextInput(self.SW * 0.65, self.SH * 0.875, 100, 50)  # Create input field instance
        self.confirm_button = Button(50, 50, "X", self.SW * 0.75, self.SH * 0.875, )
        self.start_button = Button(200, 100, "Start Game", self.SW * 0.45, self.SH * 0.75)
        self.players_lobby_display = PlayersLobbyDisplay()

        self.log_in_button = Button(300, 300, "Log in", self.SW * 0.6, self.SH * 0.3)
        self.sign_up_button = Button(300, 300, "Sign Up", self.SW * 0.3, self.SH * 0.3)

        self.players_display = PlayersDisplay()
        self.pot_display.update_text("Pot: " + str(self.pot))

        # Initialize community cards
        self.community_card_1 = CardImg(self.SW * 0.2, self.SH * 0.35)
        self.community_card_2 = CardImg(self.SW * 0.3, self.SH * 0.35)
        self.community_card_3 = CardImg(self.SW * 0.4, self.SH * 0.35)
        self.community_card_4 = CardImg(self.SW * 0.5, self.SH * 0.35)
        self.community_card_5 = CardImg(self.SW * 0.6, self.SH * 0.35)

    def setup_socket(self):
        # Set up socket connection
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect(('127.0.0.1', 8820))

    def run_pygame(self, message_queue):
        game_host = False
        page = 'start'
        print("GAME STARTED")
        buttons_hide = True
        raise_buttons_hide = True
        pressure = False
        while self.running:
            self.screen.fill((53, 101, 77))
            if page == 'start':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.log_in_button.check_click(event.pos):
                            page = 'log in'
                        if self.sign_up_button.check_click(event.pos):
                            page = 'sign up'
                self.sign_up_button.draw(self.screen)
                self.log_in_button.draw(self.screen)
            if page == 'sign up':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.submit_sign_up_button.check_click(event.pos):
                            if self.sign_up_username.get_text() and self.sign_up_password.get_text():
                                username = self.sign_up_username.get_text()
                                password = self.sign_up_password.get_text()
                                message = create_message('sign_up', (username, password), self.my_socket.getsockname())
                                self.my_socket.sendall(message.encode('utf-8'))
                                self.sign_up_password.set_text('')
                                self.sign_up_username.set_text('')
                    self.sign_up_password.handle_event(event)
                    self.sign_up_username.handle_event(event)
                self.submit_sign_up_button.draw(self.screen)
                self.sign_up_password.draw(self.screen)
                self.sign_up_username.draw(self.screen)
            if page == 'main':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.create_button.check_click(event.pos):
                            message = create_message('create', self.name, '')
                            print(message)
                            self.my_socket.sendall(message.encode('utf-8'))
                        for button in self.join_button_list.get_games():
                            if button.check_click(event.pos):
                                message = create_message('join', button[1], self.name)
                                self.my_socket.sendall(message.encode('utf-8'))
                self.join_button_list.draw(self.screen)
                self.create_button.draw(self.screen)
                mouse_pos = pygame.mouse.get_pos()
            if page == 'lobby':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.start_button.check_click(event.pos):
                            message = create_message('game-start', '', '')
                            self.my_socket.sendall(message.encode('utf-8'))
                self.players_lobby_display.draw(self.screen)
                if game_host:
                    self.start_button.draw(self.screen)
                mouse_pos = pygame.mouse.get_pos()
            if page == 'game':
                if pressure:
                    self.check_call_button.update_text("Call")
                else:
                    self.check_call_button.update_text("Check")
                # Handle events and update game screen
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.check_call_button.check_click(event.pos):
                            if pressure:
                                message = create_message('player_move', 'call', '')
                                self.my_socket.sendall(message.encode('utf-8'))
                                buttons_hide = True
                            else:
                                print("check clicked!")
                                message = create_message('player_move', 'check', '')
                                self.my_socket.sendall(message.encode('utf-8'))
                                buttons_hide = True
                            raise_buttons_hide = True
                        elif self.raise_button.check_click(event.pos):
                            raise_buttons_hide = False
                            print("RIASE BUTTONS HIDE IS FALSE")
                        elif self.confirm_button.check_click(event.pos):
                            if self.input_field.get_text():
                                value = self.input_field.get_text()
                                value = int(value)
                                if value < self.last_bet * 2:
                                    print("Raise more than the previous bet: ", self.last_bet)
                                elif value < 10:
                                    print("You can't raise less than the blinds")
                                elif value > self.chips:
                                    print("You cant raise more than what you have: ", self.chips)
                                else:
                                    message = create_message('player_move', 'raise', value)
                                    self.my_socket.sendall(message.encode('utf-8'))
                                    buttons_hide = True
                                    raise_buttons_hide = True
                                self.input_field.set_text("")
                        elif self.fold_button.check_click(event.pos):
                            message = create_message('player_move', 'fold', '')
                            self.my_socket.sendall(message.encode('utf-8'))
                            buttons_hide = True
                            raise_buttons_hide = True
                    self.input_field.handle_event(event)
                mouse_pos = pygame.mouse.get_pos()
                self.check_call_button.check_hover(mouse_pos)
                self.raise_button.check_hover(mouse_pos)
                self.fold_button.check_hover(mouse_pos)

                # Reset buttons after clicks
                self.check_call_button.reset_after_click()
                self.raise_button.reset_after_click()
                self.fold_button.reset_after_click()

                # Draw buttons and game objects
                if not buttons_hide:
                    self.check_call_button.draw(self.screen)
                    self.raise_button.draw(self.screen)
                    self.fold_button.draw(self.screen)
                if not raise_buttons_hide:
                    self.confirm_button.draw(self.screen)
                    self.input_field.draw(self.screen)
                self.community_card_1.draw(self.screen)
                self.community_card_2.draw(self.screen)
                self.community_card_3.draw(self.screen)
                self.community_card_4.draw(self.screen)
                self.community_card_5.draw(self.screen)
                self.pot_display.draw(self.screen, 5, 5)
                self.players_display.draw(self.screen)
                if self.cards:
                    self.me_display.draw(self.screen)
                self.pot_display.update_text("Pot: " + str(self.pot))

            try:
                message = message_queue.get_nowait()  # Non-blocking get from the queue
                print("RAW message: ", message)
                extra, message = self.extract_json(message)
                print("extra", extra)
                if extra:
                    message_queue.put(extra)
                message_data = json.loads(message)
                message_type = message_data.get("type")
                print("JSON message: ", message_data)
                data1 = message_data.get("data1")
                data2 = message_data.get("data2")
                if message_type == 'turn':
                    if data1 == self.name:
                        print("It's your turn!")
                        buttons_hide = False  # Enable button when it's the player's turn
                        if data2 == 'no pressure':
                            pressure = False
                        if data2 == 'pressure':
                            pressure = True
                    self.whose_turn = data1
                elif message_type == 'end_turn':
                    print("Turn ended!")
                    buttons_hide = False  # Disable button when turn ends
                elif message_type == 'round':
                    if data1 == 2:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        print(l)
                        self.community_card_1.update_img(l[0].get_img())
                        self.community_card_2.update_img(l[1].get_img())
                        self.community_card_3.update_img(l[2].get_img())
                    if data1 == 3:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        self.community_card_4.update_img(l[0].get_img())
                    if data1 == 4:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        self.community_card_5.update_img(l[0].get_img())
                elif message_type == 'pot':
                    if data1:
                        self.pot = data1

                elif message_type == 'player chips':
                    if data1 == self.name:
                        self.chips = data2
                        self.me_display.update_chips(self.chips)
                    else:
                        # index = self.players_data.index(data1) - 1
                        index = next(index for index, player in enumerate(players_data) if player[0] == data1) - 1
                        self.players_display.get_player(index).update_chips(data2)

                elif message_type == 'player-moved':
                    if data1 and data2:
                        move, val = data2
                        if val:
                            print(data1, " raised by ", val)
                        else:
                            print(data1, move, "ed")

                elif message_type == 'players':
                    if data1:
                        players_data = data1
                        self_index = next(index for index, player in enumerate(players_data) if player[0] == self.name)
                        print(self_index)
                        self.players_data = players_data[self_index:]
                        self.players_data += players_data[0:self_index]
                        self.players_display.add_players(self.players_data[1:])

                elif message_type == 'player-cards':
                    print("accsesd")
                    cards_data = message_data['data1']
                    self.chips = message_data['data2']
                    self.cards = [Card(card_data['suit'], card_data['val']) for card_data in cards_data]
                    print("CARDS", self.cards)
                    self.me_display = SelfDisplay(self.SW * 0.45, self.SH * 0.6, self.name,
                                                  self.cards[0].get_img(), self.cards[1].get_img(), str(self.chips))

                elif message_type == 'approve':
                    if data1 == 'create':
                        self.players_lobby_display.add_players(self.name)
                        page = 'lobby'
                        game_host = True

                    if data1 == 'join':
                        for name in data2:
                            self.players_lobby_display.add_players(name)
                        page = 'lobby'

                    if data1 == 'game-start':
                        page = 'game'

                    if data1 =='user':
                        page = 'main'
                        self.name = data2

                elif message_type == 'new_game':
                    self.join_button_list.add_game(data1)

                elif message_type == 'player-joined':
                    if data1 == 'lobby':
                        self.players_lobby_display.add_players(data2)

                elif message_type == 'new-round':
                    self.cards = None
                    self.players_data = None
                    self.players_display.reset()
                    self.community_card_1.reset()
                    self.community_card_2.reset()
                    self.community_card_3.reset()
                    self.community_card_4.reset()
                    self.community_card_5.reset()

            except queue.Empty:
                pass  # No message to process, simply skip

            except Exception as e:
                print(f"An error occurred: {e}")

            pygame.display.update()  # Update screen

        pygame.quit()

    def recv_data(self):
        print("Data thread started")  # Debugging message
        while True:
            # Use select.select() to check if there is data available on the socket
            readable, _, _ = select.select([self.my_socket], [], [], 0.1)
            if readable:
                message = self.my_socket.recv(1024).decode('utf-8')
                if message:
                    message_queue.put(message)

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


# Create the game object
message_queue = queue.Queue()
game = Game()

# Initialize Pygame and setup the game
game.setup_socket()
game.init_pygame()

# Start threads for game and receiving data
data_thread = threading.Thread(target=game.recv_data, daemon=True)

data_thread.start()
game.run_pygame(message_queue)
data_thread.join()
