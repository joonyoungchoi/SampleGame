from iconservice import *


values = {'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8,
          'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}


class Hand:

    def __init__(self, cards: list = None, value: int = 0, aces: int = 0, fix: bool = False):
        if cards is None:
            self.cards = []
        else:
            self.cards = cards

        self.value = value  # start with zero value
        self.aces = aces  # add an attribute to keep track of aces
        self.fix = fix

    def add_card(self, card):
        self.cards.append(card)
        self.value += values[json_loads(card)['rank']]
        if json_loads(card)['rank'] == 'Ace':
            self.aces += 1  # add to self.aces

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def __str__(self):
        response = {
            'cards': self.cards,
            'value': self.value,
            'aces': self.aces,
            'fix': self.fix
        }
        return json_dumps(response)
