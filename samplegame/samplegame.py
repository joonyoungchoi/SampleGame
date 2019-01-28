from iconservice import *

from samplegame.deck.deck import Deck
from samplegame.gameroom.gameroom import GameRoom
from samplegame.hand.hand import Hand

TAG = 'BLACKJACK'


class ChipInterface(InterfaceScore):
    """
    A class contains designated methods of Chip SCORE, enable SampleGame to use methods without implementing repeatedly.
    """

    @interface
    def mint(self, _value: int):
        pass

    @interface
    def exchange(self, amount: int):
        pass

    @interface
    def balanceOf(self, _owner: Address):
        pass

    @interface
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        pass


class SampleGame(IconScoreBase):
    """
    A main SCORE class for Blackjack
    """
    _TOKEN_ADDRESS = "token_address"
    _GAME_ROOM = "game_room"
    _GAME_ROOM_LIST = "game_room_list"
    _IN_GAME_ROOM = "in_game_room"
    _DECK = "deck"
    _HAND = "hand"
    _RESULTS = "results"

    _READY = "ready"
    _GAME_START_TIME = "game_start_time"

    def on_install(self, token_address: Address) -> None:
        super().on_install()
        if token_address.is_contract:
            self._VDB_token_address.set(token_address)
        else:
            revert("Input params must be Contract Address")

    def on_update(self, **kwargs) -> None:
        super().on_update()
        pass

    def __init__(self, db: 'IconScoreDatabase') -> None:
        super().__init__(db)
        self._db = db
        self._VDB_token_address = VarDB(self._TOKEN_ADDRESS, db, value_type=Address)
        self._DDB_game_room = DictDB(self._GAME_ROOM, db, value_type=str)
        self._DDB_game_start_time = DictDB(self._GAME_START_TIME, db, value_type=int)
        self._DDB_in_game_room = DictDB(self._IN_GAME_ROOM, db, value_type=Address)
        self._DDB_deck = DictDB(self._DECK, db, value_type=str)
        self._DDB_hand = DictDB(self._HAND, db, value_type=str)
        self._DDB_ready = DictDB(self._READY, db, value_type=bool)

    def _get_game_room_list(self):
        return ArrayDB(self._GAME_ROOM_LIST, self._db, value_type=str)

    def _get_results(self):
        return ArrayDB(self._RESULTS, self._db, value_type=str)

    @external(readonly=True)
    def show_game_room_list(self) -> list:
        response = []
        game_room_list = self._get_game_room_list()

        for game_room in game_room_list:
            game_room_id = json_loads(game_room)['game_room_id']
            creation_time = json_loads(game_room)['creation_time']
            prize_per_game = json_loads(game_room)['prize_per_game']
            participants = json_loads(game_room)['participants']
            room_joinable = "Full" if len(participants) < 2 else "Joinable"
            response.append(f"{game_room_id} : ({len(participants)} / 2). The room is now {room_joinable}. Prize : {prize_per_game}. Creation time : {creation_time}")

        return response

    @external
    def create_room(self, prize_per_game: int = 10):
        # Check whether 'self.msg.sender' is now participating to game room or not
        if self._DDB_in_game_room[self.msg.sender] is not None:
            revert("You already joined to another room")

        # Check whether the chip balance of 'self.msg.sender' exceeds the prize_per_game or not
        chip = self.create_interface_score(self._VDB_token_address.get(), ChipInterface)
        if chip.balanceOf(self.msg.sender) < prize_per_game:
            revert("Set the prize not to exceed your balance")

        # Create the game room & Get in to it & Set the prize_per_game value
        game_room = GameRoom(self.msg.sender, self.msg.sender, self.block.height, prize_per_game)
        game_room.join(self.msg.sender)
        self._DDB_game_room[self.msg.sender] = str(game_room)

        game_room_list = self._get_game_room_list()
        game_room_list.put(str(game_room))
        self._DDB_in_game_room[self.msg.sender] = self.msg.sender

        # Initialize the deck of participant
        new_deck = Deck()
        self._DDB_deck[self.msg.sender] = str(new_deck)
        new_hand = Hand()
        self._DDB_hand[self.msg.sender] = str(new_hand)

    def _crash_room(self, game_room_id: Address):
        game_room_to_crash_dict = json_loads(self._DDB_game_room[game_room_id])
        list(self._get_game_room_list()).remove(json_dumps(game_room_to_crash_dict))

    @external
    def join_room(self, game_room_id: Address):
        # Check whether the game room with game_room_id is existent or not
        if game_room_id not in self._get_game_room_list():
            revert(f"There is no game room created by {game_room_id}")

        # Check the participant is already joined to another game_room
        if self._DDB_in_game_room[self.msg.sender] is not None:
            revert(f"You already joined to another game room : {self._DDB_in_game_room[self.msg.sender]}")

        game_room_dict = json_loads(self._DDB_game_room[game_room_id])
        game_room = GameRoom(game_room_dict['owner'], game_room_dict['game_room_id'], game_room_dict['creation_time'],
                             game_room_dict['prize_per_game'], game_room_dict['participants'], game_room_dict['active'])

        # Check the chip balance of 'self.msg.sender' before getting in
        chip = self.create_interface_score(self._VDB_token_address.get(), ChipInterface)
        if chip.balanceOf(self.msg.sender) < game_room.prize_per_game:
            revert(
                f"Not enough Chips to join this game room {game_room_id}. Require {game_room.prize_per_game} chips")

        # Check the game room's participants. Max : 2
        if len(game_room.participants) > 1:
            revert(f"Full : Can not join to game room {game_room_id}")

        # Get in to the game room
        game_room.join(self.msg.sender)
        self._DDB_in_game_room[self.msg.sender] = game_room_id
        self._DDB_game_room[game_room_id] = str(game_room)

        # Initialize the deck & hand of participant
        new_deck = Deck()
        self._DDB_deck[self.msg.sender] = str(new_deck)
        new_hand = Hand()
        self._DDB_hand[self.msg.sender] = str(new_hand)

    @external
    def escape(self):
        # Check whether 'self.msg.sender' is now participating to game room or not
        if self._DDB_in_game_room[self.msg.sender] is None:
            revert(f'No game room to escape')

        # Retrieve the game room ID & Check the game room status
        game_room_id_to_escape = self._DDB_in_game_room[self.msg.sender]
        game_room_to_escape_dict = json_loads(self._DDB_game_room[game_room_id_to_escape])
        game_room_to_escape = GameRoom(game_room_to_escape_dict['owner'], game_room_to_escape_dict['game_room_id'],
                                       game_room_to_escape_dict['creation_time'], game_room_to_escape_dict['prize_per_game'],
                                       game_room_to_escape_dict['participants'], game_room_to_escape_dict['active'])
        if game_room_to_escape.active:
            revert("The game is not finalized yet.")

        # Escape from the game room
        if game_room_to_escape.owner == self.msg.sender and len(game_room_to_escape.participants) == 1:
            game_room_to_escape.escape(self.msg.sender)
            self._crash_room(game_room_id_to_escape)
        else:
            game_room_to_escape.escape(self.msg.sender)
            self._DDB_game_room[game_room_id_to_escape] = str(game_room_to_escape)

        # Set the in_game_room status of 'self.msg.sender' to None
        self._DDB_in_game_room[self.msg.sender] = None

    @external
    def toggle_ready(self):
        if self._DDB_in_game_room[self.msg.sender] is None:
            revert("Enter the game room first.")
        if self._DDB_ready[self.msg.sender]:
            self._DDB_ready[self.msg.sender] = False
        else:
            self._DDB_ready[self.msg.sender] = True

    @external
    def game_start(self):
        game_room_id = self._DDB_in_game_room[self.msg.sender]
        game_room_dict = json_loads(self._DDB_game_room[game_room_id])
        game_room = GameRoom(game_room_dict['owner'], game_room_dict['game_room_id'], game_room_dict['creation_time'],
                             game_room_dict['prize_per_game'], game_room_dict['participants'], game_room_dict['active'])
        participants = game_room.participants

        # Check the 'self.msg.sender' == game_room.owner
        if not self.msg.sender == game_room.owner:
            revert("Only owner of game room can start the game")

        # Check the number of participants
        if len(participants) < 2:
            revert("Please wait for a challenger to come")

        # Make sure that all the participants are ready
        for participant in participants:
            if not self._DDB_ready[participant]:
                revert(f"{participant} is not ready to play game")

        # Game start
        game_room.game_start()
        self._DDB_game_start_time[game_room_id] = self.block.height
        self._DDB_game_room[game_room_id] = str(game_room)

        # Set ready status of both participants to False after starting the game
        for participant in participants:
            self._DDB_ready[participant] = False

    @external(readonly=True)
    def show_mine(self) -> str:
        if self._DDB_in_game_room[self.msg.sender] in None:
            revert("You are not in game")

        hand = self._DDB_hand[self.msg.sender]
        return hand

    @external
    def hit(self):
        game_room_id = self._DDB_in_game_room[self.msg.sender]
        game_room_dict = self._DDB_game_room[game_room_id]
        game_room = GameRoom(game_room_dict['owner'], game_room_dict['game_room_id'], game_room_dict['creation_time'],
                             game_room_dict['prize_per_game'], game_room_dict['participants'], game_room_dict['active'])

        # Check whether the game is in active mode or not
        if not game_room.active:
            revert("The game is now in inactive mode")

        # Hit and adjust the status of deck & hand
        deck_dict = json_loads(self._DDB_deck[self.msg.sender])
        deck = Deck(deck_dict['deck'])
        hand_dict = json_loads(self._DDB_hand[self.msg.sender])
        hand = Hand(hand_dict['cards'], hand_dict['value'], hand_dict['aces'], hand_dict['fix'])

        # Check if the participant has already fixed hands
        if hand.fix:
            revert('You already fixed your hand')

        # Revert if the participant already has 5 cards.
        if len(hand.cards) > 4:
            revert(f"You can have cards up to 5")

        if len(hand.cards) == 4:
            hand.fix = True

        hand.add_card(deck.deal())
        hand.adjust_for_ace()
        self._DDB_deck[self.msg.sender] = str(deck)
        self._DDB_hand[self.msg.sender] = str(hand)

        # Check whether the fix status of all participants are True. And, If participant 'hand.value' exceeds 21, finalize the game. & Game must be finalized.
        if self._check_participants_fix(game_room_id) or hand.value > 21 or self.block.height - self._DDB_game_start_time[game_room_id] > 60:
            self.calculate(game_room_id)

    def _check_participants_fix(self, game_room_id: Address) -> bool:
        game_room_dict = self._DDB_game_room[game_room_id]
        game_room = GameRoom(game_room_dict['owner'], game_room_dict['game_room_id'], game_room_dict['creation_time'],
                             game_room_dict['prize_per_game'], game_room_dict['participants'], game_room_dict['active'])
        participants = game_room.participants

        for participant in participants:
            hand_dict = json_loads(self._DDB_hand[participant])
            hand = Hand(hand_dict['cards'], hand_dict['value'], hand_dict['aces'], hand_dict['fix'])
            if not hand.fix:
                return False

        return True

    @external
    def fix(self):
        hand_dict = json_loads(self._DDB_hand[self.msg.sender])
        hand = Hand(hand_dict['cards'], hand_dict['value'], hand_dict['aces'], hand_dict['fix'])
        hand.fix = True
        self._DDB_hand[self.msg.sender] = str(hand)

    @external
    def calculate(self, game_room_id: Address = None):
        chip = self.create_interface_score(self._VDB_token_address.get(), ChipInterface)
        if game_room_id is None:
            game_room_id = self._DDB_in_game_room[self.msg.sender]

        # Finalize the game
        self._game_stop(game_room_id)

        # Calculate the result
        game_room_dict = json_loads(self._DDB_game_room[game_room_id])
        game_room = GameRoom(game_room_dict['owner'], game_room_dict['game_room_id'], game_room_dict['creation_time'],
                             game_room_dict['prize_per_game'], game_room_dict['participants'], game_room_dict['active'])
        participants = game_room.participants
        participant_gen = (participant for participant in participants)
        first_participant = next(participant_gen)
        first_hand_dict = json_loads(self._DDB_hand[first_participant])
        first_hand = Hand(first_hand_dict['cards'], first_hand_dict['value'], first_hand_dict['aces'], first_hand_dict['fix'])
        second_participant = next(participant_gen)
        second_hand_dict = json_loads(self._DDB_hand[second_participant])
        second_hand = Hand(second_hand_dict['cards'], second_hand_dict['value'], second_hand_dict['aces'], second_hand_dict['fix'])

        results = self._get_results()
        if first_hand.value > 21 or second_hand.value > 21:
            chip.transfer(first_participant, game_room.prize_per_game * 2) if second_hand.value>21 else chip.transfer(second_participant, game_room.prize_per_game * 2)
            results.put(f"{first_participant} wins against {second_participant}.")
        elif first_hand.value > second_hand.value:
            chip.transfer(first_participant, game_room.prize_per_game * 2)
            results.put(f"{first_participant} wins against {second_participant}.")
        elif first_hand.value < second_hand.value:
            chip.transfer(second_participant, game_room.prize_per_game * 2)
            results.put(f"{second_participant} wins against {first_participant}.")
        else:
            chip.transfer(first_participant, game_room.prize_per_game)
            chip.transfer(second_participant, game_room.prize_per_game)
            results.put(f"Draw!! {first_participant}, {second_participant}.")

    def _game_stop(self, game_room_id):
        game_room_dict = json_loads(self._DDB_game_room[game_room_id])
        game_room = GameRoom(game_room_dict['owner'], game_room_dict['game_room_id'], game_room_dict['creation_time'],
                             game_room_dict['prize_per_game'], game_room_dict['participants'], game_room_dict['active'])
        game_room.game_stop()
        self._DDB_game_room[game_room_id] = str(game_room)

    @external(readonly=True)
    def get_results(self) -> str:
        return json_dumps(self._get_results())

    @external
    @payable
    def mint_chips(self):
        chip = self.create_interface_score(self._VDB_token_address.get(), ChipInterface)
        chip.mint(self.msg.value)

    @external
    def exchange(self, amount: int):
        chip = self.create_interface_score(self._VDB_token_address.get(), ChipInterface)
        chip.exchange(amount)
