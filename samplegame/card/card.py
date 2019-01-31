from iconservice import *


class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        response = {
            'suit': self.suit,
            'rank': self.rank
        }
        return json_dumps(response)