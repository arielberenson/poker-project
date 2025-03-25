import random


# https://cardscans.piwigo.com/index?/category/706-g
# https://nicubunu.ro/graphics:playingcards


class User:
    def __init__(self, client_socket, client_address, username=None, password=None, chips=None):
        self.username = username
        self.password = password
        self.socket = client_socket
        self.address = client_address
        self.chips = chips

    def get_socket(self):
        return self.socket

    def get_chips(self):
        return self.chips

    def get_address(self):
        return self.address

    def get_username(self):
        return self.username

    def create_account(self, username, password, chips):
        self.username = username
        self.password = password
        self.chips = chips


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

    def new_game(self):
        self.round_bet = 0
        self.cards = []

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
        self.new_deck()

    def new_deck(self):
        self.cards = []
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
