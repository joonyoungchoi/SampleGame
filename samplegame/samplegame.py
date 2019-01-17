from iconservice import IconScoreBase, IconScoreDatabase


class SampleGame(IconScoreBase):

    def on_install(self, **kwargs) -> None:
        super().on_install()
        pass

    def on_update(self, **kwargs) -> None:
        super().on_update()
        pass

    def __init__(self, db: 'IconScoreDatabase') -> None:
        super().__init__(db)
        self._db = db
        pass
