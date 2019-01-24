from iconservice import Address, json_dumps, json_loads


class GameRoom:

    def __init__(self, _game_room_id: Address, _creation_time: int):
        self._game_room_id = _game_room_id
        self._creation_time = _creation_time
        pass

    def __str__(self):
        response = {
            'game_room_id': f'{self._game_room_id}',
            'creation_time': f'{self._creation_time}'
        }
        return json_dumps(response)
