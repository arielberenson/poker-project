import random


class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val
        self.img = 'images/deck/white_{}_{}.svg'.format(suit.lower(), val)

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


class Communal:
    def __init__(self):
        self.cards = []

    def get_cards(self):
        return self.cards

    def clear(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)
