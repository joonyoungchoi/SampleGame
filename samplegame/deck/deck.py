from iconservice import *

from ..card.card import Card

suits = ('Hearts', 'Diamonds', 'Spades', 'Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')


class Deck:

    def __init__(self, deck: list = None):
        self.deck = deck
        # If deck is empty list, fill the deck with cards
        if self.deck is None:
            self.deck = []
            for suit in suits:
                for rank in ranks:
                    self.deck.append(str(Card(suit, rank)))

    def deal(self, block_height: int, sender_address: Address):
        deal_input = str(block_height) + str(sender_address)
        random_index = int.from_bytes(bytes(sha3_256(deal_input.encode())), 'big') % len(self.deck)
        single_card = self.deck.pop(random_index)
        return single_card

    def __str__(self):
        response = {
            'deck': self.deck
        }
        return json_dumps(response)
