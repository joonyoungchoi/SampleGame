from _sha256 import sha256

from samplegame.deck.card.card import Card

suits = ('Hearts', 'Diamonds', 'Spades', 'Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')


class Deck:

    def __init__(self):
        self.deck = []  # start with an empty list
        for suit in suits:
            for rank in ranks:
                self.deck.append(Card(suit, rank))

    def deal(self):
        random_index = int.from_bytes(bytes(sha256("some unique things".encode()).digest()), 'big') % len(self.deck)
        single_card = self.deck.pop(random_index)
        return single_card
