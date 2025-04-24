import threading
import socket
from poker_classes import Card
from pygame_classes import *
from extra_functions import *
import select
import queue


class Client:
    def __init__(self):
        # misc
        self.whose_turn = None
        self.me_display = None
        self.running = True
        self.pot = None
        self.game_over = None
        self.players_data = None
        self.last_bet = 0
        self.my_socket = None
        self.name = None
        self.cards = None
        # log in / sign up
        self.log_in_button = Button(sw * 0.25, sh * 0.3, "Log in", sw * 0.55, sh * 0.3)
        self.sign_up_button = Button(sw * 0.25, sh * 0.3, "Sign Up", sw * 0.2, sh * 0.3)

        self.sign_up_username = TextInput(sw * 0.3, sh * 0.4, sw * 0.4, sh * 0.15)
        self.sign_up_password = TextInput(sw * 0.3, sh * 0.6, sw * 0.4, sh * 0.15)
        self.submit_sign_up_button = Button(sw * 0.15, sh * 0.15, "Submit", sw * 0.4, sh * 0.8)

        # home page
        self.create_button = Button(200, 200, "Create", sw * 0.60, sh * 0.3)
        self.welcome_display = TextDisplay(36, (0, 0, 0), "Hi, ")
        self.join_button_list = GamesDisplay()

        # lobby
        self.start_button = Button(200, 100, "Start Game", sw * 0.45, sh * 0.75)
        self.players_lobby_display = PlayersLobbyDisplay()

        # game - moves
        self.check_call_button = Button(100, 50, "Check", sw * 0.35, sh * 0.875)
        self.raise_button = Button(100, 50, "Raise", sw * 0.45, sh * 0.875)
        self.fold_button = Button(100, 50, "Fold", sw * 0.55, sh * 0.875)

        # game - raise
        self.slider = Slider(sw * 0.65, sh * 0.875, 100, 0, 100, 50)
        self.confirm_button = Button(50, 50, "X", sw * 0.75, sh * 0.875, )

        # game
        self.chips_display = ChipsDisplay(sw * 0.2, sh * 0.1, "1000")
        self.leave_game_button = Button(100, 50, "Leave", sw * 0.7, sh * 0.1)
        self.play_again_button = Button(400, 400, "Play Again?", sw * 0.3, sh * 0.3)
        self.pot_display = TextDisplay(36, (0, 0, 0), "[Pot]")
        self.players_display = PlayersDisplay()

        # Initialize community cards
        self.community_cards = CardImages(sw * 0.29, sh * 0.2)
        self.screen = pygame.display.set_mode((sw, sh))

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption('Poker Game')

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
            if page == 'log in':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.submit_sign_up_button.check_click(event.pos):
                            if self.sign_up_username.get_text() and self.sign_up_password.get_text():
                                username = self.sign_up_username.get_text()
                                password = self.sign_up_password.get_text()
                                message = create_message('log_in', (username, password), self.my_socket.getsockname())
                                self.my_socket.sendall(message.encode('utf-8'))
                                self.sign_up_password.set_text('')
                                self.sign_up_username.set_text('')
                    self.sign_up_password.handle_event(event)
                    self.sign_up_username.handle_event(event)
                self.submit_sign_up_button.draw(self.screen)
                self.sign_up_password.draw(self.screen)
                self.sign_up_username.draw(self.screen)
            if page == 'main':
                game_host = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.create_button.check_click(event.pos):
                            message = create_message('create', self.name, '')
                            print(message)
                            self.my_socket.sendall(message.encode('utf-8'))
                        for game in self.join_button_list.get_games():
                            if game[0].check_click(event.pos):
                                message = create_message('join', game[1], self.name)
                                self.my_socket.sendall(message.encode('utf-8'))
                self.join_button_list.draw(self.screen)
                self.create_button.draw(self.screen)
                self.chips_display.draw(self.screen, sw * 0.1, sh * 0.1)
                self.welcome_display.draw(self.screen, sw * 0.3, sh * 0.1)
                self.welcome_display.update_text("Hi, " + self.name)
                self.chips_display.update_chips(self.chips)
                mouse_pos = pygame.mouse.get_pos()
            if page == 'lobby':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.start_button.check_click(event.pos):
                            message = create_message('start_game', '', '')
                            self.my_socket.sendall(message.encode('utf-8'))
                        if self.leave_game_button.check_click(event.pos):
                            message = create_message('leave_game', self.name, game_host)
                            self.my_socket.sendall(message.encode('utf-8'))
                            page = 'main'
                self.leave_game_button.draw(self.screen)
                self.players_lobby_display.draw(self.screen)
                if game_host and self.players_lobby_display.count() > 1:
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
                            if self.slider.get_value():
                                value = self.slider.get_value()
                                value = int(value)
                                message = create_message('player_move', 'raise', value)
                                self.my_socket.sendall(message.encode('utf-8'))
                                buttons_hide = True
                                raise_buttons_hide = True
                        elif self.fold_button.check_click(event.pos):
                            message = create_message('player_move', 'fold', '')
                            self.my_socket.sendall(message.encode('utf-8'))
                            buttons_hide = True
                            raise_buttons_hide = True
                        elif self.play_again_button.check_click(event.pos):
                            message = create_message('play_again', '', '')
                            self.my_socket.sendall(message.encode('utf-8'))
                        if self.leave_game_button.check_click(event.pos):
                            message = create_message('leave_game', self.name, '')
                            self.my_socket.sendall(message.encode('utf-8'))
                            page = 'main'
                    self.slider.update(event)
                mouse_pos = pygame.mouse.get_pos()
                self.leave_game_button.draw(self.screen)
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
                    self.slider.set_max_value(min(self.pot*2, self.chips, 5))
                    self.slider.set_min_value(self.last_bet*2)
                if not raise_buttons_hide:
                    self.confirm_button.draw(self.screen)
                    self.slider.draw(self.screen)
                self.community_cards.draw(self.screen)
                self.pot_display.draw(self.screen, 5, 5)
                self.players_display.draw(self.screen)
                if self.cards:
                    self.me_display.draw(self.screen)
                self.pot_display.update_text("Pot: " + str(self.pot))

                if self.game_over and game_host:
                    self.play_again_button.draw(self.screen)

            try:
                message = message_queue.get_nowait()  # Non-blocking get from the queue
                print("RAW message: ", message)
                extra, message = extract_json(message)
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
                    self.last_bet = 0
                    if data1 == 2:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        print(l)
                        for i in range(2):
                            self.community_cards.update_img(i, l[i].get_img())
                    if data1 == 3:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        self.community_cards.update_img(3, l[0].get_img())
                    if data1 == 4:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        self.community_cards.update_img(4, l[0].get_img())
                elif message_type == 'pot':
                    if data1:
                        self.pot = data1

                elif message_type == 'player chips':
                    if data1 == self.name:
                        self.chips = data2
                        self.me_display.update_chips(self.chips)
                    else:
                        # index = self.players_data.index(data1) - 1
                        index = next(index for index, player in enumerate(self.players_data) if player[0] == data1) - 1
                        self.players_display.get_player(index).update_chips(data2)

                elif message_type == 'player_left':
                    if page == 'lobby':
                        self.players_lobby_display.remove_player(data1)
                    else:
                        self.players_display.remove_player(data1)

                elif message_type == 'remove_game':
                    self.join_button_list.remove_game(data1)

                elif message_type == 'game_host':
                    game_host = True

                elif message_type == 'game_over':
                    self.game_over = True

                elif message_type == 'player_moved':
                    if data1 and data2:
                        move, val = data2
                        if val:
                            print(data1, " raised by ", val)
                            self.last_bet = val
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

                elif message_type == 'player_cards':
                    print("accsesd")
                    cards_data = message_data['data1']
                    self.chips = message_data['data2']
                    self.cards = [Card(card_data['suit'], card_data['val']) for card_data in cards_data]
                    print("CARDS", self.cards)
                    self.me_display = SelfDisplay(sw * 0.45, sh * 0.45, self.name,
                                                  self.cards[0].get_img(), self.cards[1].get_img(), str(self.chips))

                elif message_type == 'approve':
                    if data1 == 'create':
                        self.players_lobby_display.clear()
                        self.players_lobby_display.add_players(self.name)
                        page = 'lobby'
                        game_host = True

                    if data1 == 'join':
                        self.players_lobby_display.clear()
                        for name in data2:
                            self.players_lobby_display.add_players(name)
                        page = 'lobby'

                    if data1 == 'start_game':
                        page = 'game'
                        self.new_game()

                    if data1 == 'user':
                        page = 'main'
                        self.name = data2[0]
                        self.chips = data2[1]

                    if data1 == 'log in':
                        page = 'main'
                        self.name = data2[0]
                        self.chips = data2[1]

                elif message_type == 'new_game':
                    self.join_button_list.add_game(data1, data2)

                elif message_type == 'player_joined':
                    if data1 == 'lobby':
                        self.players_lobby_display.add_players(data2)

                elif message_type == 'play_again':
                    self.new_game()

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

    def new_game(self):
        self.cards = None
        self.players_data = None
        self.players_display.reset()
        self.community_cards.reset()
        self.game_over = False
        self.pot = 0


sw, sh = get_screen_info()

# Create the game object
message_queue = queue.Queue()
client = Client()

# Initialize Pygame and setup the game
client.setup_socket()
client.init_pygame()

# Start threads for game and receiving data
data_thread = threading.Thread(target=client.recv_data, daemon=True)

data_thread.start()
client.run_pygame(message_queue)
data_thread.join()
