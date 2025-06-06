import threading
import socket
from classes.game_classes.deck import Card
from classes.pygame_structure import *
from database.firebase_client import get_server_ip_from_firebase
from extra_functions import *
import select
import queue


class Client:
    def __init__(self):
        # misc
        self.pressure = False
        self.chips = None
        self.whose_turn = None
        self.me_display = None
        self.running = True
        self.pots = [0]
        self.game_over = None
        self.players_data = None
        self.highest_round_bet = 0
        self.player_round_bet = 0
        self.my_socket = None
        self.name = None
        self.cards = None
        self.game_host = False
        self.all_in = False
        self.me_display = None
        # log in / sign up
        self.log_in_button = Button(sw * 0.25, sh * 0.3, "Log in", sw * 0.55, sh * 0.3)
        self.sign_up_button = Button(sw * 0.25, sh * 0.3, "Sign Up", sw * 0.2, sh * 0.3)

        self.restart_button = Button(100, 50, "Back", sw * 0.7, sh * 0.1)
        self.username_input = TextInput(sw * 0.3, sh * 0.35, sw * 0.4, sh * 0.13)
        self.password_input = TextInput(sw * 0.3, sh * 0.55, sw * 0.4, sh * 0.13)
        self.username_text = TextDisplay()
        self.password_text = TextDisplay()
        self.username_text.update_text("Username: ")
        self.password_text.update_text("Password: ")
        self.error_message = TextDisplay()
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
        self.slider = Slider(sw * 0.65, sh * 0.875, sw*0.27, 5, 100, 50)
        self.confirm_button = Button(50, 50, "OK", sw * 0.93, sh * 0.875, )

        # game
        self.chips_display = ChipsDisplay(sw * 0.2, sh * 0.1, "333")
        self.leave_game_button = Button(100, 50, "Leave", sw * 0.7, sh * 0.1)
        self.play_again_button = Button(100, 50, "Play Again?", sw * 0.5, sh * 0.5)

        self.pots_display = PotDisplay(sw * 0.1, sh * 0.1)
        self.players_display = PlayersDisplay()
        self.showdown_info = ShowdownInfoDisplay()

        # Initialize community cards
        self.community_cards = CardImages(sw * 0.29, sh * 0.2)
        self.screen = pygame.display.set_mode((sw, sh))

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption('Poker Game')

    def setup_socket(self):
        # Set up socket connection
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_ip = get_server_ip_from_firebase()
        server_port = 8820
        self.my_socket.connect((server_ip, server_port))

    def run_pygame(self, message_queue):
        self.game_host = False
        page = 'start'
        print("GAME STARTED")
        buttons_hide = True
        raise_buttons_hide = True
        self.pressure = False
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
                            if self.username_input.get_text() and self.password_input.get_text():
                                username = self.username_input.get_text()
                                password = self.password_input.get_text()
                                message = create_message('sign_up', username, password)
                                self.my_socket.sendall(message)
                                self.password_input.set_text('')
                                self.username_input.set_text('')
                        if self.restart_button.check_click(event.pos):
                            page = 'start'
                    self.password_input.handle_event(event)
                    self.username_input.handle_event(event)
                self.submit_sign_up_button.draw(self.screen)
                self.password_input.draw(self.screen)
                self.username_input.draw(self.screen)
                self.username_text.draw(self.screen, sw*0.3, sh*0.3)
                self.password_text.draw(self.screen, sw*0.3, sh*0.5)
                self.restart_button.draw(self.screen)
            if page == 'log in':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.submit_sign_up_button.check_click(event.pos):
                            if self.username_input.get_text() and self.password_input.get_text():
                                username = self.username_input.get_text()
                                password = self.password_input.get_text()
                                message = create_message('log_in', username, password)
                                self.my_socket.sendall(message)
                                self.password_input.set_text('')
                                self.username_input.set_text('')
                        if self.restart_button.check_click(event.pos):
                            page = 'start'
                    self.password_input.handle_event(event)
                    self.username_input.handle_event(event)
                self.submit_sign_up_button.draw(self.screen)
                self.password_input.draw(self.screen)
                self.username_input.draw(self.screen)
                self.username_text.draw(self.screen, sw*0.3, sh*0.3)
                self.password_text.draw(self.screen, sw*0.3, sh*0.5)
                self.restart_button.draw(self.screen)
            if page == 'main':
                self.game_host = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.create_button.check_click(event.pos):
                            message = create_message('create', '', '')
                            print(message)
                            self.my_socket.sendall(message)
                        for game in self.join_button_list.get_games():
                            if game[0].check_click(event.pos):
                                message = create_message('join', game[1], '')
                                self.my_socket.sendall(message)
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
                            self.my_socket.sendall(message)
                        if self.leave_game_button.check_click(event.pos):
                            message = create_message('leave_game', self.name, self.game_host)
                            self.my_socket.sendall(message)
                            page = 'main'
                self.leave_game_button.draw(self.screen)
                self.players_lobby_display.draw(self.screen)
                if self.game_host and self.players_lobby_display.count() > 1:
                    self.start_button.draw(self.screen)
                mouse_pos = pygame.mouse.get_pos()
            if page == 'game':
                if self.pressure:
                    if self.highest_round_bet - self.player_round_bet > self.chips:
                        self.check_call_button.update_text(f"Call [{self.chips}]")
                    else:
                        self.check_call_button.update_text(f"Call [{self.highest_round_bet - self.player_round_bet}]")
                    # print("Highest: ", self.highest_round_bet)
                    # print("Self: ", self.player_round_bet)
                else:
                    self.check_call_button.update_text("Check")
                # Handle events and update game screen
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.check_call_button.check_click(event.pos):
                            if self.pressure:
                                value = self.highest_round_bet - self.player_round_bet
                                message = create_message('player_move', 'call', value)
                                self.my_socket.sendall(message)
                                buttons_hide = True
                                self.player_round_bet = self.highest_round_bet
                            else:
                                print("check clicked!")
                                message = create_message('player_move', 'check', '')
                                self.my_socket.sendall(message)
                                buttons_hide = True
                            raise_buttons_hide = True
                        elif self.raise_button.check_click(event.pos):
                            raise_buttons_hide = not raise_buttons_hide
                            print("RIASE BUTTONS HIDE IS FALSE")
                        elif self.confirm_button.check_click(event.pos):
                            if self.slider.get_value():
                                value = int(self.slider.get_value() + self.highest_round_bet)
                                message = create_message('player_move', 'raise', value)
                                self.my_socket.sendall(message)
                                self.player_round_bet += value
                                buttons_hide = True
                                raise_buttons_hide = True
                        elif self.fold_button.check_click(event.pos):
                            message = create_message('player_move', 'fold', '')
                            self.my_socket.sendall(message)
                            buttons_hide = True
                            raise_buttons_hide = True
                        elif self.play_again_button.check_click(event.pos):
                            message = create_message('play_again', '', '')
                            self.my_socket.sendall(message)
                        if self.leave_game_button.check_click(event.pos):
                            message = create_message('leave_game', self.name, '')
                            self.my_socket.sendall(message)
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
                if not self.game_over:
                    if not buttons_hide:
                        self.check_call_button.draw(self.screen)
                        self.raise_button.draw(self.screen)
                        self.fold_button.draw(self.screen)
                        self.slider.set_max_value(min(self.pots[0] * 2 - self.player_round_bet, self.chips - self.highest_round_bet))
                        if self.highest_round_bet == 0:
                            self.slider.set_min_value(5)
                        else:
                            self.slider.set_min_value(self.highest_round_bet)
                    if not raise_buttons_hide:
                        self.confirm_button.draw(self.screen)
                        self.slider.draw(self.screen)
                    self.community_cards.draw(self.screen)
                    self.pots_display.draw(self.screen, self.pots)
                    self.players_display.draw(self.screen)
                    if self.cards:
                        self.me_display.draw(self.screen)
                else:
                    self.showdown_info.draw(self.screen)
                    if self.game_host:
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
                        self.highest_round_bet = data2
                        if self.highest_round_bet - self.player_round_bet > 0:
                            self.pressure = True
                        else:
                            self.pressure = False

                    self.whose_turn = data1

                elif message_type == 'end_turn':
                    print("Turn ended!")
                    buttons_hide = False  # Disable button when turn ends

                elif message_type == 'round':
                    self.highest_round_bet = 0
                    self.player_round_bet = 0
                    if data1 == 2:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        print(l)
                        for i in range(3):
                            self.community_cards.update_img(i, l[i].get_img())
                    if data1 == 3:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        self.community_cards.update_img(3, l[0].get_img())
                    if data1 == 4:
                        l = [Card(card_data['suit'], card_data['val']) for card_data in data2]
                        self.community_cards.update_img(4, l[0].get_img())

                elif message_type == 'pots':
                    new_pot = data1
                    if len(new_pot) > len(self.pots):
                        self.pots_display.add_pot(new_pot[-1])
                    self.pots = data1

                elif message_type == 'player_chips':
                    if data1 == self.name:
                        self.chips = data2
                        self.me_display.update_chips(self.chips)
                    else:
                        self.players_display.get_player(data1).update_chips(data2)

                elif message_type == 'player_left':
                    if page == 'lobby':
                        self.players_lobby_display.remove_player(data1)
                    else:
                        self.players_display.remove_player(data1)

                elif message_type == 'remove_game':
                    self.join_button_list.remove_game(data1)

                elif message_type == 'self.game_host':
                    self.game_host = True

                elif message_type == 'game_over':
                    self.game_over = True
                    data = []
                    for player in data2:
                        cards_data = player[1]
                        cards = [Card(card_data['suit'], card_data['val']) for card_data in cards_data]
                        data.append((player[0], cards))
                    self.showdown_info.update(data1, data)

                elif message_type == 'player_moved':
                    if data1 and data2:
                        move, val = data2
                        if val:
                            print(data1, " raised by ", val)
                        else:
                            print(data1, move, "ed")

                elif message_type == 'players':
                    if data1:
                        players_data = data1
                        self.showdown_info.set_old_chips(players_data)
                        self_index = next(index for index, player in enumerate(players_data) if player[0] == self.name)
                        print(self_index)
                        self.players_data = players_data[self_index:]
                        self.players_data += players_data[0:self_index]
                        print(self.players_data[1:])
                        self.players_display.add_players(self.players_data[1:])

                elif message_type == 'player_cards':
                    cards_data = message_data['data1']
                    self.chips = message_data['data2']
                    self.cards = [Card(card_data['suit'], card_data['val']) for card_data in cards_data]
                    print("CARDS", self.cards)
                    self.me_display = SelfDisplay(sw * 0.41, sh * 0.45, self.name,
                                                  self.cards[0].get_img(), self.cards[1].get_img(), str(self.chips))

                elif message_type == 'approve':
                    if data1 == 'create':
                        self.players_lobby_display.clear()
                        self.players_lobby_display.add_players(self.name)
                        page = 'lobby'
                        self.game_host = True

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

                    if data1 == 'log_in':
                        page = 'main'
                        self.name = data2[0]
                        self.chips = data2[1]

                elif message_type == 'reject':
                    if data1 == 'log_in':
                        self.error_message.update_text("Error logging in. Check your username and password")
                    if data1 == 'sign_up':
                        self.error_message.update_text("Error signing up. Username might already exist.")

                elif message_type == 'new_game':
                    self.join_button_list.add_game(data1, data2)

                elif message_type == 'player_joined':
                    if data1 == 'lobby':
                        self.players_lobby_display.add_players(data2)

                elif message_type == 'play_again':
                    self.new_game()
                    page = 'game'

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
                message = self.my_socket.recv(1024)
                decrypted_message = decrypt(message)
                if decrypted_message:
                    message_queue.put(decrypted_message)

    def new_game(self):
        self.cards = None
        self.players_data = None
        self.players_display.reset()
        self.community_cards.reset()
        self.showdown_info.reset()
        self.game_over = False
        self.pressure = False
        self.pots = [0]
        self.highest_round_bet = 0
        self.player_round_bet = 0


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
