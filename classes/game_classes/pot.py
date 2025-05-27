class Pot:
    def __init__(self):
        self.chips = 0

    def add_chips(self, n):
        self.chips += n

    def clear_pot(self):
        self.chips = 0

    def get_chips(self):
        return self.chips


class PotList:
    def __init__(self):
        self.pots = [Pot()]

    def add_chips(self, i, n):
        self.pots[i].add_chips(n)

    def clear_pot(self, i):
        self.pots[i].clear_pot()

    def clear_all(self):
        self.pots = [Pot()]

    def get_chips(self, i):
        return self.pots[i].get_chips()

    def get_length(self):
        return len(self.pots)
