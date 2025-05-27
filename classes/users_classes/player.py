class Player:
    def __init__(self, user, username, chips, spectating=False, allin=False):
        self.user = user
        self.cards = []
        self.username = username
        self.chips = chips
        self.round_bet = 0
        self.active = False
        self.spectating = spectating
        self.allin = allin

    def is_allin(self):
        return self.allin

    def set_allin(self, allin):
        self.allin = allin

    def remove_chips(self, n):
        self.chips -= int(n)
        self.round_bet += int(n)

    def add_chips(self, n):
        self.chips += n

    def is_active(self):
        return self.active

    def set_active(self, b):
        self.active = b

    def new_game(self):
        self.round_bet = 0
        self.cards = []
        self.active = True

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
