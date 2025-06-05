class Pot:
    def __init__(self):
        self.chips = 0
        self.actions = []
        self.allin = []
        self.players = []

    def set_players(self, players):
        self.players = players

    def add_chips(self, n):
        self.chips += n

    def is_allin(self):
        return self.allin

    def clear_pot(self):
        self.chips = 0

    def get_chips(self):
        return self.chips

    def add_action(self, player, n, info=""):
        if player not in self.players:
            self.players.append(player)
        self.actions.append([player, n, info])
        self.add_chips(n)
        if info == "allin":
            self.allin = True

    def get_actions(self):
        return self.actions

    def clear_actions(self):
        self.allin = False
        self.actions = []

    def set_allin(self, param):
        self.allin = []

    def get_allin_action(self):
        for action in self.actions:
            if action[2] == "allin":
                return action
        return False

    def create_allin_instance(self, amount, allin_player):
        new_pot = Pot()
        allin = [[allin_player, amount]]
        for player in self.players:
            if player == allin_player:
                continue
            if player.get_round_bet() > amount:
                allin.append([player, amount])
                new_pot.add_chips(player.get_round_bet() - amount)
            if player.get_round_bet() == amount:
                allin.append([player, amount])
            else:
                allin.append([player, player.get_round_bet()])
        self.allin = allin
        return new_pot

    def get_allin(self):
        return self.allin


class PotList:
    def __init__(self):
        self.players = None
        self.pots = [Pot()]

    def add_chips(self, n, i=-1):
        self.pots[i].add_chips(n)

    def clear_pot(self, i):
        self.pots[i].clear_pot()

    def clear_all(self):
        self.pots = [Pot()]

    def clear_actions(self):
        for pot in self.pots:
            pot.clear_actions()

    def add_action(self, player, n, i=-1, info=""):
        pot = self.pots[0]
        data = pot.get_allin()
        if data:
            print(data)
            ceiling = data[0][1]
            for item in data:
                if item[0] == player:
                    if item[1] + n > ceiling:
                        pot.add_action(player, ceiling - item[1])
                        if len(self.pots) == 1:
                            new_pot = Pot()
                            new_pot.add_action(player, n - (ceiling - item[1]), info)
                            self.pots.append(new_pot)
                            item[1] = ceiling
                            return new_pot
                        else:
                            self.pots[1].add_action(player, n - (ceiling - item[1]), info)
                            item[1] = ceiling
                            return False
                    pot.add_action(player, n, info)
                    item[1] += n
                    return False
        else:
            pot.add_action(player, n, info)
            return False

    # min meaning how much the player could bet (player chips) and max meaning the amount needed to call
    def side_pot(self, player, min_x, max_x):
        new_pot = Pot()
        og_pot = self.pots[-1]
        og_pot.add_action(player, min_x)
        if min_x < max_x:
            for (p, n) in og_pot.get_actions():
                if n > min_x:
                    new_pot.add_action(p, n - min_x)
                    og_pot.add_chips(min_x - n)
        self.pots.append(new_pot)
        og_pot.set_allin(True)
        return og_pot, new_pot

    def create_allin(self, player, min_x, max_x):
        og_pot = self.pots[-1]
        og_pot.add_action(player, min_x)
        new_pot = og_pot.create_allin_instance(min_x, player)
        if new_pot.get_chips() > 0:
            self.pots.append(new_pot)
            return new_pot
        return False

    def get_chips(self, i=-1):
        return self.pots[i].get_chips()

    def get_length(self):
        return len(self.pots)

    def get_pots(self):
        return self.pots

    def get_allin_type(self):
        for pot in self.pots:
            if pot.is_allin():
                if pot == self.pots[-1]:
                    return 1
                else:
                    return 2
        return 0

    def make_new_pot(self, player, n):
        pot = Pot()
        pot.add_action(player, n)
        self.pots.append(pot)
        return self.pots[-2].get_chips(), pot.get_chips()

    def add_multiple_pot_action(self, player, n):
        action = self.pots[-2].get_allin_action()
        if not action:
            return
