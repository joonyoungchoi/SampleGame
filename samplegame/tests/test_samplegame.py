import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import (
    DeployTransactionBuilder,
    CallTransactionBuilder,
    TransactionBuilder)
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice import Address, json_loads
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestSampleGame(IconIntegrateTestBase):
    SAMPLE_GAME_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))
    CHIP_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '../../chip'))

    def setUp(self):
        print("---------------------setup-------------------------")
        super().setUp()

        self.icon_service = None
        # self.icon_service = IconService(HTTPProvider("http://localhost:9000/api/v3"))

        self.test1_wallet = self._test1
        self.test2_wallet = self._wallet_array[0]
        self.test3_wallet = self._wallet_array[1]
        wallet_list = [self.test1_wallet, self.test2_wallet, self.test3_wallet]

        # install SCORE
        self.decimals = 0
        params_for_chip = {
            '_decimals': self.decimals
        }
        # self._chip_score_address = 'cx20a25e2d114ee9c80ee45fca83911a663cf5ed22'
        self._chip_score_address = self._deploy_score(content=self.CHIP_PROJECT, params=params_for_chip)['scoreAddress']

        params_for_sample_game = {
            '_tokenAddress': self._chip_score_address
        }
        # self._sample_game_score_address = 'cx4623bb6f4604e488a70b5c609c60fa860ed4e825'
        self._sample_game_score_address = self._deploy_score(params=params_for_sample_game)['scoreAddress']

        for wallet in wallet_list:
            self._transfer(wallet.get_address())
            self._mint_chips(_from=wallet, amount=11)

    def tearDown(self):
        print("---------------------------------------------------")

    def _transfer(self, to: str):
        transaction = TransactionBuilder().from_(self.test1_wallet.get_address()) \
            .to(to) \
            .step_limit(10_000_000) \
            .nid(3) \
            .value(1_000_000_000) \
            .build()

        signed_transaction = SignedTransaction(transaction, self.test1_wallet)

        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS, content: str = SAMPLE_GAME_PROJECT, params: dict = None) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self.test1_wallet.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(content)) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self.test1_wallet)

        # process the transaction
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def _show_game_room_list(self, _from: KeyWallet):
        call = CallBuilder().from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .method("showGameRoomList") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        return response

    def _get_chip_balance(self, _from: KeyWallet):
        call = CallBuilder().from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .method("getChipBalance") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        return response

    def _create_room(self, _from: KeyWallet):
        transaction_create_room = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("createRoom") \
            .params('') \
            .build()

        signed_transaction_create_room = SignedTransaction(transaction_create_room, _from)
        tx_result_create_room = self.process_transaction(signed_transaction_create_room, self.icon_service)
        return tx_result_create_room

    def _join_room(self, _from: KeyWallet, _game_room_id: Address):
        transaction_join_room = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("joinRoom") \
            .params({'_gameRoomId': f'{_game_room_id}'}) \
            .build()

        signed_transaction_join_room = SignedTransaction(transaction_join_room, _from)
        tx_result_join_room = self.process_transaction(signed_transaction_join_room, self.icon_service)
        return tx_result_join_room

    def _escape(self, _from: KeyWallet):
        transaction_escape_room = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("escape") \
            .params({}) \
            .build()

        signed_transaction_escape_room = SignedTransaction(transaction_escape_room, _from)
        tx_result_escape_room = self.process_transaction(signed_transaction_escape_room, self.icon_service)
        return tx_result_escape_room

    def _toggle_ready(self, _from: KeyWallet):
        transaction_toggle_ready = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("toggleReady") \
            .params({}) \
            .build()

        signed_transaction_toggle_ready = SignedTransaction(transaction_toggle_ready, _from)
        tx_result_toggle_ready = self.process_transaction(signed_transaction_toggle_ready, self.icon_service)
        return tx_result_toggle_ready

    def _game_start(self, _from: KeyWallet):
        transaction_game_start = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("gameStart") \
            .params({}) \
            .build()

        signed_transaction_game_start = SignedTransaction(transaction_game_start, _from)

        tx_result_game_start = self.process_transaction(signed_transaction_game_start, self.icon_service)
        return tx_result_game_start

    def _hit(self, _from: KeyWallet):
        transaction_hit = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("hit") \
            .params('') \
            .build()

        signed_transaction_hit = SignedTransaction(transaction_hit, _from)

        tx_result_hit = self.process_transaction(signed_transaction_hit, self.icon_service)
        return tx_result_hit

    def _fix(self, _from: KeyWallet):
        transaction_fix = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("fix") \
            .params('') \
            .build()

        signed_transaction_fix = SignedTransaction(transaction_fix, _from)

        tx_result_fix = self.process_transaction(signed_transaction_fix, self.icon_service)
        return tx_result_fix

    def _show_mine(self, _from: KeyWallet = KeyWallet.create()):
        call = CallBuilder().from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .method("showMine") \
            .build()

        response = self.process_call(call, self.icon_service)
        return response

    def _get_results(self, _from: KeyWallet):
        call = CallBuilder().from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .method("getResults") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        return response

    def _mint_chips(self, _from: KeyWallet, amount: int):
        transaction_mint_chips = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .value(amount) \
            .nonce(100) \
            .method("mintChips") \
            .params('') \
            .build()

        signed_transaction_mint_chips = SignedTransaction(transaction_mint_chips, _from)
        tx_result_mint = self.process_transaction(signed_transaction_mint_chips, self.icon_service)
        return tx_result_mint

    def _exchange(self, _from: KeyWallet, amount: int):
        params = {
            'amount': amount
        }

        transaction_exchange = CallTransactionBuilder() \
            .from_(_from.get_address()) \
            .to(self._sample_game_score_address) \
            .step_limit(10_000_000) \
            .nid(3) \
            .nonce(100) \
            .method("exchange") \
            .params(params) \
            .build()

        signed_transaction_exchange = SignedTransaction(transaction_exchange, _from)

        tx_result_exchange = self.process_transaction(signed_transaction_exchange, self.icon_service)
        return tx_result_exchange

    def test_score_update(self):
        # update SCORE
        print('Update')
        tx_result = self._deploy_score(to=self._sample_game_score_address)

        self.assertEqual(self._sample_game_score_address, tx_result['scoreAddress'])

    def test_scenario1(self):
        call = CallBuilder().from_(self.test1_wallet.get_address()) \
            .to(self._sample_game_score_address) \
            .method("showGameRoomList") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        print(response)

        tx_result_create_room = self._create_room(self.test1_wallet)
        self.assertTrue('status' in tx_result_create_room)
        self.assertEqual(1, tx_result_create_room['status'])

        tx_result_create_room = self._create_room(self.test2_wallet)
        self.assertTrue('status' in tx_result_create_room)
        self.assertEqual(1, tx_result_create_room['status'])

        tx_result_create_room = self._create_room(self.test1_wallet)
        self.assertTrue('status' in tx_result_create_room)
        self.assertEqual(0, tx_result_create_room['status'])

        call = CallBuilder().from_(self.test1_wallet.get_address()) \
            .to(self._sample_game_score_address) \
            .method("showGameRoomList") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        print(response)

    def test_scenario2(self):

        tx_result_create_room = self._create_room(self.test1_wallet)
        self.assertTrue('status' in tx_result_create_room)
        self.assertEqual(1, tx_result_create_room['status'])

        result_show_game_room_list = self._show_game_room_list(self.test1_wallet)
        print(result_show_game_room_list)
        self.assertEqual(1, len(result_show_game_room_list))

        tx_result_join_room = self._join_room(self.test2_wallet, self.test1_wallet.get_address())
        self.assertTrue('status' in tx_result_join_room)
        self.assertEqual(1, tx_result_join_room['status'])

        tx_result_join_room = self._join_room(self.test3_wallet, self.test1_wallet.get_address())
        self.assertTrue('status' in tx_result_join_room)
        self.assertEqual(0, tx_result_join_room['status'])

        tx_result_escape_room = self._escape(self.test1_wallet)
        self.assertTrue('status' in tx_result_escape_room)
        self.assertEqual(0, tx_result_escape_room['status'])

        tx_result_escape_room = self._escape(self.test2_wallet)
        self.assertTrue('status' in tx_result_escape_room)
        self.assertEqual(1, tx_result_escape_room['status'])

        tx_result_join_room = self._join_room(self.test3_wallet, self.test1_wallet.get_address())
        self.assertTrue('status' in tx_result_join_room)
        self.assertEqual(1, tx_result_join_room['status'])

        tx_result_escape_room = self._escape(self.test3_wallet)
        self.assertTrue('status' in tx_result_escape_room)
        self.assertEqual(1, tx_result_escape_room['status'])

        result_show_game_room_list = self._show_game_room_list(self.test1_wallet)
        self.assertEqual(1, len(result_show_game_room_list))

        tx_result_escape_room = self._escape(self.test1_wallet)
        self.assertTrue('status' in tx_result_escape_room)
        self.assertEqual(1, tx_result_escape_room['status'])

        result_show_game_room_list = self._show_game_room_list(self.test1_wallet)
        self.assertEqual(0, len(result_show_game_room_list))

    def test_scenario3(self):
        self._create_room(self.test1_wallet)
        self._join_room(self.test2_wallet, self.test1_wallet.get_address())

        result_show_game_room_list = self._show_game_room_list(self.test1_wallet)
        print(result_show_game_room_list)

        tx_result_toggle_ready = self._toggle_ready(self.test1_wallet)
        self.assertTrue('status' in tx_result_toggle_ready)
        self.assertEqual(1, tx_result_toggle_ready['status'])

        tx_result_game_start = self._game_start(self.test1_wallet)
        self.assertTrue('status' in tx_result_game_start)
        self.assertEqual(0, tx_result_game_start['status'])

        tx_result_toggle_ready = self._toggle_ready(self.test2_wallet)
        self.assertTrue('status' in tx_result_toggle_ready)
        self.assertEqual(1, tx_result_toggle_ready['status'])

        tx_result_hit = self._hit(self.test1_wallet)
        self.assertTrue('status' in tx_result_hit)
        self.assertEqual(0, tx_result_hit['status'])

        tx_result_game_start = self._game_start(self.test2_wallet)
        self.assertTrue('status' in tx_result_game_start)
        self.assertEqual(0, tx_result_game_start['status'])

        tx_result_game_start = self._game_start(self.test1_wallet)
        self.assertTrue('status' in tx_result_game_start)
        self.assertEqual(1, tx_result_game_start['status'])
        print(tx_result_game_start)

        tx_result_game_start = self._game_start(self.test1_wallet)
        self.assertTrue('status' in tx_result_game_start)
        self.assertEqual(0, tx_result_game_start['status'])

        tx_result_escape = self._escape(self.test1_wallet)
        self.assertTrue('status' in tx_result_escape)
        self.assertEqual(0, tx_result_escape['status'])

        tx_result_hit = self._hit(self.test1_wallet)
        self.assertTrue('status' in tx_result_hit)
        self.assertEqual(1, tx_result_hit['status'])

        result_show_mine = self._show_mine(self.test1_wallet)
        print(result_show_mine)

        tx_result_hit = self._hit(self.test2_wallet)
        self.assertTrue('status' in tx_result_hit)
        self.assertEqual(1, tx_result_hit['status'])

        result_show_mine = self._show_mine(self.test2_wallet)
        print(result_show_mine)

        tx_result_fix = self._fix(self.test1_wallet)
        self.assertTrue('status' in tx_result_fix)
        self.assertEqual(1, tx_result_fix['status'])

        tx_result_fix = self._fix(self.test2_wallet)
        self.assertTrue('status' in tx_result_fix)
        self.assertEqual(1, tx_result_fix['status'])

        result_get_results = self._get_results(self.test1_wallet)
        print(result_get_results)

        result_show_game_room_list = self._show_game_room_list(self.test1_wallet)
        print(result_show_game_room_list)

    def test_scenario4(self):
        self._create_room(self.test1_wallet)
        self._join_room(self.test2_wallet, self.test1_wallet.get_address())

        tx_result_toggle_ready = self._toggle_ready(self.test1_wallet)
        self.assertTrue('status' in tx_result_toggle_ready)
        self.assertEqual(1, tx_result_toggle_ready['status'])

        tx_result_game_start = self._game_start(self.test1_wallet)
        self.assertTrue('status' in tx_result_game_start)
        self.assertEqual(0, tx_result_game_start['status'])

        tx_result_toggle_ready = self._toggle_ready(self.test2_wallet)
        self.assertTrue('status' in tx_result_toggle_ready)
        self.assertEqual(1, tx_result_toggle_ready['status'])

        tx_result_hit = self._hit(self.test1_wallet)
        self.assertTrue('status' in tx_result_hit)
        self.assertEqual(0, tx_result_hit['status'])

        tx_result_game_start = self._game_start(self.test2_wallet)
        self.assertTrue('status' in tx_result_game_start)
        self.assertEqual(0, tx_result_game_start['status'])

        tx_result_game_start = self._game_start(self.test1_wallet)
        self.assertTrue('status' in tx_result_game_start)
        self.assertEqual(1, tx_result_game_start['status'])

        tx_result_escape = self._escape(self.test1_wallet)
        self.assertTrue('status' in tx_result_escape)
        self.assertEqual(0, tx_result_escape['status'])

        for _ in range(5):
            tx_result_hit = self._hit(self.test1_wallet)
            self.assertTrue('status' in tx_result_hit)
            self.assertEqual(1, tx_result_hit['status'])

            result_show_mine = self._show_mine(self.test1_wallet)
            if json_loads(result_show_mine)['value'] > 21:
                break

            tx_result_hit = self._hit(self.test2_wallet)
            self.assertTrue('status' in tx_result_hit)
            self.assertEqual(1, tx_result_hit['status'])

            result_show_mine = self._show_mine(self.test2_wallet)
            if json_loads(result_show_mine)['value'] > 21:
                break

        result_get_results = self._get_results(self.test2_wallet)
        print(result_get_results)

        result_show_game_room_list = self._show_game_room_list(self.test2_wallet)
        print(result_show_game_room_list)

    def test_scenario5(self):
        tx_result_exchange = self._exchange(self.test1_wallet, 10)
        self.assertTrue('status' in tx_result_exchange)
        self.assertEqual(1, tx_result_exchange['status'])

        tx_result_exchange = self._exchange(self.test1_wallet, 10)
        self.assertTrue('status' in tx_result_exchange)
        self.assertEqual(0, tx_result_exchange['status'])

        tx_result_create_room = self._create_room(self.test1_wallet)
        self.assertTrue('status' in tx_result_create_room)
        self.assertEqual(0, tx_result_create_room['status'])

        tx_result_create_room = self._create_room(self.test2_wallet)
        self.assertTrue('status' in tx_result_create_room)
        self.assertEqual(1, tx_result_create_room['status'])

        tx_result_join_room = self._join_room(self.test1_wallet, self.test2_wallet.get_address())
        self.assertTrue('status' in tx_result_join_room)
        self.assertEqual(0, tx_result_join_room['status'])
