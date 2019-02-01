from iconservice import *


class GameRoom:

    def __init__(self, _owner: Address, _game_room_id: Address, _creation_time: int, _prize_per_game: int, _participants: list = None, _active: bool = False):
        self.owner = _owner
        self.game_room_id = _game_room_id
        self.creation_time = _creation_time
        self.prize_per_game = _prize_per_game
        if _participants is None:
            self.participants = []
        else:
            self.participants = _participants
        self.active = _active

    def join(self, _participant: Address):
        self.participants.append(str(_participant))

    def escape(self, _participant_to_escape: Address):
        self.participants.remove(str(_participant_to_escape))

    def game_start(self):
        self.active = True

    def game_stop(self):
        self.active = False

    def __str__(self):
        response = {
            'owner': f'{self.owner}',
            'game_room_id': f'{self.game_room_id}',
            'creation_time': self.creation_time,
            'prize_per_game': self.prize_per_game,
            'participants': self.participants,
            'active': self.active
        }
        return json_dumps(response)
