from iconservice import *

TAG = 'Blackjack'


class TokenFallbackInterface(InterfaceScore):
    @interface
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        pass


class Chip(IconScoreBase):
    _BALANCES = 'balances'
    _TOTAL_SUPPLY = 'total_supply'
    _DECIMALS = 'decimals'

    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):
        pass

    def on_install(self, decimals: int) -> None:
        super().on_install()

        self._total_supply.set(0)
        self._decimals.set(decimals)

    def on_update(self) -> None:
        super().on_update()
        pass

    def __init__(self, db: 'IconScoreDatabase') -> None:
        super().__init__(db)
        self._balances = DictDB(self._BALANCES, db, value_type=int)
        self._decimals = VarDB(self._DECIMALS, db, value_type=int)
        self._total_supply = VarDB(self._TOTAL_SUPPLY, db, value_type=int)

    @external(readonly=True)
    def name(self) -> str:
        """
        :return: The name of Token.
        """
        return "blackjack chips"

    @external(readonly=True)
    def symbol(self) -> str:
        """
        :return: The symbol of Token.
        """
        return "chips"

    @external(readonly=True)
    def decimals(self) -> int:
        """
        :return: The value of decimals. [Chip * 10 ** decimals = ICX]
        """
        return self._decimals.get()

    @external(readonly=True)
    def totalSupply(self) -> int:
        """
        :return: The overall amount of minted chips for game
        """
        return self._total_supply.get()

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        """
        :param _owner: The owner of Chips
        :return: The amount of chips owned by _owner
        """
        return self._balances[_owner]

    @external
    @payable
    def mint(self, _value):
        """
        This method should be invoked by CA not EOA.

        :param _value: The amount of Chips to mint
        """
        if self.msg.sender.is_contract:
            self._balances[self.tx.origin] = self._balances[self.tx.origin] + _value
        else:
            revert("This method should be invoked by CA not EOA")

    @external
    def exchange(self, amount: int):
        """
        This method should be invoked by CA not EOA.

        :param amount: the amount of Chips to exchange for icx
        """
        if self.msg.sender.is_contract:
            pass
        else:
            revert("This method should be invoked by CA not EOA")

        if self._balances[self.tx.origin] > amount:
            self._balances[self.tx.origin] = self._balances[self.tx.origin] - amount
            self.icx.send(self.tx.origin, amount)

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        if _value < 0:
            revert('Transferring value cannot be less than zero')
        if self._balances[self.tx.origin] < _value:
            revert("Out of balance")

        self._balances[self.tx.origin] = self._balances[self.tx.origin] - _value
        self._balances[_to] = self._balances[_to] + _value

        # Emits an event log `Transfer`
        self.Transfer(self.tx.origin, _to, _value, _data)
        Logger.debug(f'Transfer({self.tx.origin},{_to},{_value},{_data})', TAG)
