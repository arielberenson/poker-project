from classes import *
from classes.users_classes.player import Player
from classes.users_classes.user import User
from extra_functions import create_message
from classes.game_classes.pot import PotList

u1 = User('socket', 'address', 'ariel', 100)
p1 = Player(u1, 'ariel', 100)

u2 = User('socket', 'address', 'maya', 50)
p2 = Player(u2, 'maya', 50)

u3 = User('socket', 'address', 'asaf', 20)
p3 = Player(u3, 'asaf', 20)

players = [p1, p2, p3]
pots = PotList()


def place_bet(player, n, last_bet=None):
    if n >= player.get_chips():
        old, new = pots.side_pot(player, player.get_chips(), n)
        player.remove_chips(player.get_chips())
        player.set_allin(True)
    else:
        player.remove_chips(n)
        pots.add_action(player, n)
    if last_bet < n:
        last_bet = n


def show():
    for p in players:
        print(p.get_username() + p.get_chips())
    for pot in pots.get_pots():
        print(pot.get_chips())


place_bet(p1, 30)
show()
place_bet(p2, 30)
