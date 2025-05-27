class Pot:
    def __init__(self):
        self.chips = 0
        self.actions = []

    def add_chips(self, n):
        self.chips += n

    def clear_pot(self):
        self.chips = 0

    def get_chips(self):
        return self.chips

    def add_action(self, player, n):
        self.actions.append([player, n])
        self.add_chips(n)

    def get_actions(self):
        return self.actions

    def clear_actions(self):
        self.actions = []


class PotList:
    def __init__(self):
        self.pots = [Pot()]

    def add_chips(self, n, i=0):
        self.pots[i].add_chips(n)

    def clear_pot(self, i):
        self.pots[i].clear_pot()

    def clear_all(self):
        self.pots = [Pot()]

    def clear_actions(self):
        for pot in self.pots:
            pot.clear_actions()

    def add_action(self, player, n, i=0):
        self.pots[i].add_action(player, n)

    def side_pot(self, player, initial):
        new_pot = Pot()
        og_pot = self.pots[-1]
        new_pot.add_action(player, initial)
        for (p, n) in og_pot.get_actions():
            if n > initial:
                new_pot.add_action(p, initial)
                temp = initial - n
                og_pot.add_chips(temp)
        self.pots.append(Pot())

    def get_chips(self, i=0):
        return self.pots[i].get_chips()

    def get_length(self):
        return len(self.pots)
