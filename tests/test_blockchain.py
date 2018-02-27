import hashlib
import json
from unittest import TestCase

from blockchain import Blockchain


class BlockchainTestCase(TestCase):

    def setUp(self):
        self.blockchain = Blockchain()

    def create_new_block(self, proof=123, prev_hash='abc'):
        self.blockchain.create_new_block(proof, prev_hash)

    def create_new_transaction(self, sender='a', receiver='b', amount=1):
        self.blockchain.create_new_transaction(
            sender=sender,
            receiver=receiver,
            amount=amount
        )


class TestRegisterNodes(BlockchainTestCase):

    def test_valid_nodes(self):
        blockchain = Blockchain()

        blockchain.register_node('http://192.168.0.1:5000')

        self.assertIn('192.168.0.1:5000', blockchain.nodes)

    # TODO: Not sure what this test is supposed to check and how it's different from test_valid_nodes
    # def test_malformed_nodes(self):
    #     blockchain = Blockchain()
    #
    #     blockchain.register_node('http//192.168.0.1:5000')
    #
    #     self.assertNotIn('192.168.0.1:5000', blockchain.nodes)

    def test_idempotency(self):
        blockchain = Blockchain()

        blockchain.register_node('http://192.168.0.1:5000')
        blockchain.register_node('http://192.168.0.1:5000')

        assert len(blockchain.nodes) == 1


class TestBlocksAndTransactions(BlockchainTestCase):

    def test_block_creation(self):
        self.create_new_block()

        latest_block = self.blockchain.latest_block

        # The genesis block is create at initialization, so the length should be 2
        assert len(self.blockchain.chain) == 2
        assert latest_block['index'] == 1
        assert latest_block['timestamp'] is not None
        assert latest_block['proof'] == 123
        assert latest_block['prev_hash'] == 'abc'

    def test_create_new_transaction(self):
        self.create_new_transaction()

        transaction = self.blockchain.utxo[-1]

        assert transaction
        assert transaction['sender'] == 'a'
        assert transaction['receiver'] == 'b'
        assert transaction['amount'] == 1

    def test_block_resets_transactions(self):
        self.create_new_transaction()

        initial_length = len(self.blockchain.utxo)

        self.create_new_block()

        current_length = len(self.blockchain.utxo)

        assert initial_length == 1
        assert current_length == 0

    def test_return_last_block(self):
        self.create_new_block()

        created_block = self.blockchain.latest_block

        assert len(self.blockchain.chain) == 2
        assert created_block is self.blockchain.chain[-1]


class TestHashingAndProofs(BlockchainTestCase):

    def test_hash_is_correct(self):
        self.create_new_block()

        latest_block = self.blockchain.latest_block
        latest_block_json = json.dumps(self.blockchain.latest_block, sort_keys=True).encode()
        latest_hash = hashlib.sha256(latest_block_json).hexdigest()

        assert len(latest_hash) == 64
        assert latest_hash == self.blockchain.calculate_hash(latest_block)