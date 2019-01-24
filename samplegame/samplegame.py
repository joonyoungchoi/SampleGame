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
    _GAME_ROOM_PARTICIPANTS = "game_room_participants"
    _GAME_ROOM_LIST = "game_room_list"
    _GAME_ACTIVE = "game_active"
    _IN_GAME_ROOM = "in_game_room"
    _TOKEN_ADDRESS = "token_address"
    _PRIZE_PER_GAME = "prize_per_game"
    _DECK = "deck"
    _HAND = "hand"
    _READY = "ready"
    _GAME_START_TIME = "game_start_time"
    _RESULTS = "results"

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
        self._VDB_results = VarDB(self._RESULTS, db, value_type=str)
        self._VDB_token_address = VarDB(self._TOKEN_ADDRESS, db, value_type=Address)
        self._DDB_game_room_participants = DictDB(self._GAME_ROOM_PARTICIPANTS, db, value_type=str)
        self._DDB_in_game_room = DictDB(self._IN_GAME_ROOM, db, value_type=Address)
        self._DDB_prize_per_game = DictDB(self._PRIZE_PER_GAME, db, value_type=int)
        self._DDB_deck = DictDB(self._DECK, db, value_type=str)
        self._DDB_hand = DictDB(self._HAND, db, value_type=str)
        self._DDB_game_active = DictDB(self._GAME_ACTIVE, db, value_type=bool)
        self._DDB_ready = DictDB(self._READY, db, value_type=bool)
        self._DDB_game_start_time = DictDB(self._GAME_START_TIME, db, value_type=int)

    def get_game_room_list(self):
        return ArrayDB(self._GAME_ROOM_LIST, self._db, value_type=str)

    @external(readonly=True)
    def show_game_room_list(self) -> list:
        response = []
        game_room_list = self.get_game_room_list()

        for game_room in game_room_list:
            game_room_id = json_loads(game_room)['game_room_id']
            creation_time = json_loads(game_room)['creation_time']
            participants = self._DDB_game_room_participants[game_room_id]
            prize_per_game = self._DDB_prize_per_game[game_room_id]
            status = "Full"
            if len(participants) < 2:
                status = "Joinable"
            response.append(f"{game_room_id} : ({len(
                participants)} / 2). The room is now {status}. Prize : {prize_per_game}. Creation time : {creation_time}")

        return response

    @external
    def create_room(self, prize_per_game: int):
        # Check whether 'self.msg.sender' is now participating to game room or not
        if self._DDB_in_game_room[self.msg.sender] is not None:
            revert("You already joined to another room")

        # Check whether the chip balance of 'self.msg.sender' exceeds the prize_per_game or not
        chip = self.create_interface_score(self._VDB_token_address.get(), ChipInterface)
        if chip.balanceOf(self.msg.sender) < prize_per_game:
            revert("Set the prize not to exceed your balance")

        # Create the game room & Get in to it & Set the prize_per_game value
        game_room = GameRoom(self.msg.sender, self.block.height)
        game_room_list = self.get_game_room_list()
        game_room_list.put(str(game_room))
        self._DDB_game_room_participants[self.msg.sender] = json_dumps([self.msg.sender])
        self._DDB_in_game_room[self.msg.sender] = self.msg.sender
        self._DDB_prize_per_game[self.msg.sender] = prize_per_game

        # Set the status of game_active to True
        self._DDB_game_active[self.msg.sender] = False

        # Initialize the deck of participant
        new_deck = Deck()
        self._DDB_deck[self.msg.sender] = json_dumps(new_deck)
        new_hand = Hand()
        self._DDB_hand[self.msg.sender] = json_dumps(new_hand)

    @external
    def join_room(self, game_room_id: Address):
        # Check whether the game room created by 'host_address' is existent or not
        if self._DDB_game_room_participants[game_room_id] == "":
            revert(f"There is no game room created by {game_room_id}")

        # Check the chip balance of 'self.msg.sender' before getting in
        chip = self.create_interface_score(self._VDB_token_address.get(), ChipInterface)
        if chip.balanceOf(self.msg.sender) < self._DDB_prize_per_game[game_room_id]:
            revert(f"Not enough Chips to join this game room {game_room_id}. Require {self._DDB_prize_per_game} chips")

        # Check the game room's participants. Max : 2
        participants = json_loads(self._DDB_game_room_participants[game_room_id])
        if len(participants) > 1:
            revert(f"Full : Can not join to game room created by {game_room_id}")

        # Get in to the game room
        participants.append(self.msg.sender)
        self._DDB_in_game_room[self.msg.sender] = game_room_id
        self._DDB_game_room_participants[game_room_id] = json_dumps(participants)

        # Initialize the deck & hand of participant
        new_deck = Deck()
        self._DDB_deck[self.msg.sender] = json_dumps(new_deck)
        new_hand = Hand()
        self._DDB_hand[self.msg.sender] = json_dumps(new_hand)

    @external
    def escape(self):
        # Check whether 'self.msg.sender' is now participating to game room or not
        if self._DDB_in_game_room[self.msg.sender] is None:
            revert(f'No game room to escape')

        # Retrieve the game room ID & Check the game room status
        game_room_to_escape = self._DDB_in_game_room[self.msg.sender]
        if self._DDB_game_active[game_room_to_escape]:
            revert("The game is not finalized yet.")

        # Escape from the game room
        participants = json_loads(self._DDB_game_room_participants[game_room_to_escape])
        participants.remove(self.msg.sender)
        self._DDB_game_room_participants[game_room_to_escape] = json_dumps(participants)

        # Set the in_game_room status of 'self.msg.sender' to None
        self._DDB_in_game_room[self.msg.sender] = None

    @external
    def get_ready(self):
        if self._DDB_in_game_room[self.msg.sender] is None:
            revert("Enter the game room first.")
        self._DDB_ready[self.msg.sender] = True

    @external
    def game_start(self):
        game_room = self._DDB_in_game_room[self.msg.sender]
        participants = json_loads(self._DDB_game_room_participants[game_room])

        # Check the number of participants
        if len(participants) < 2:
            revert("Please wait for a challenger to come")

        # Make sure that all the participants are ready
        for participant in participants:
            if not self._DDB_ready[participant]:
                revert(f"{participant} is not ready to play game")

        # Game start
        self._DDB_game_active[game_room] = True
        self._DDB_game_start_time[game_room] = self.block.height

        # Set ready status of both participants to False after starting the game
        for participant in participants:
            self._DDB_ready[participant] = False

    @external(readonly=True)
    def show_mine(self) -> str:
        if self._DDB_in_game_room[self.msg.sender] in None:
            revert("You are not in any of game")

        hand = self._DDB_hand[self.msg.sender]
        return str(hand)

    @external
    def hit(self):
        game_room = self._DDB_in_game_room[self.msg.sender]

        # Check whether the game is in active mode or not
        if not self._DDB_game_active[game_room]:
            revert("The game is now in inactive mode")

        # Hit and adjust the status of deck & hand
        deck = json_loads(self._DDB_deck[self.msg.sender])
        hand = json_loads(self._DDB_hand[self.msg.sender])

        # Revert if the participant already has 3 cards.
        if len(hand) > 2:
            revert(f"You can have cards up to 3")

        hand.add_card(deck.deal())
        hand.adjust_for_ace()
        self._DDB_deck[self.msg.sender] = json_dumps(deck)
        self._DDB_hand[self.msg.sender] = json_dumps(hand)

        self.calculate(game_room)
        # If 'hand.value' exceeds 21, finalize the game.
        if hand.value > 21:
            self.calculate(game_room)

        # Game must be finalized.
        if self.block.height - self._DDB_game_start_time[game_room] > 30:
            self.calculate(game_room)

    @external
    def calculate(self, game_room: Address = None):
        chip = self.create_interface_score(self._VDB_token_address.get(), ChipInterface)
        if game_room is None:
            game_room = self._DDB_in_game_room[self.msg.sender]

        # Finalize the game
        self._game_stop(game_room)

        # Calculate the result
        participants = json_loads(self._DDB_game_room_participants[game_room])
        participant_gen = (participant for participant in participants)
        first_participant = next(participant_gen)
        first_hand = json_loads(self._DDB_hand[first_participant])
        second_participant = next(participant_gen)
        second_hand = json_loads(self._DDB_hand[second_participant])

        results = self._VDB_results.get()
        if first_hand.value > second_hand.value:
            chip.transfer(first_participant, self._DDB_prize_per_game[game_room] * 2)
            self._VDB_results.set(
                results + f"\n{first_participant} wins against {second_participant}. {self.block.height}")
        elif first_hand.value < second_hand.value:
            chip.transfer(second_participant, self._DDB_prize_per_game[game_room] * 2)
            self._VDB_results.set(
                results + f"\n{second_participant} wins against {first_participant}. {self.block.height}")
        else:
            chip.transfer(first_participant, self._DDB_prize_per_game[game_room])
            chip.transfer(second_participant, self._DDB_prize_per_game[game_room])
            self._VDB_results.set(results + f"\nDraw!! {first_participant}, {second_participant}. {self.block.height}")

    def _game_stop(self, game_room):
        self._DDB_game_active[game_room] = False

    @external(readonly=True)
    def get_result(self) -> str:
        return self._VDB_results.get()
