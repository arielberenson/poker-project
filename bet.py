def place_bet(players, pot,  n):
    players.get_current().remove_chips(n - players.get_current().get_round_bet())
    pot.add_chips(n)
    if players.get_last_bet() < n:
        players.set_last_bet(n)


def fold(players):
    players.remove_first_player()


def check(players):
    players.next_player()
