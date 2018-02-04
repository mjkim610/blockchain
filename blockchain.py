import hashlib
import json
from time import time


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.utxo = []

        # Create the Genesis Block
        self.create_new_block(proof=1337, prev_hash=1337)

    @property
    def latest_block(self):
        return self.chain[-1]

    @staticmethod
    def calculate_hash(block):
        """
        Calculate SHA-256 hash of a Block

        :param block: <dict> Block to calculate hash for
        :return: <str> hash value
        """

        # Sort the dictionary to get consistent results
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()

    def create_new_block(self, proof, prev_hash):
        """
        Create a new Block in the Chain

        :param proof: <int> Proof found using the Proof of Work algorithm
        :param prev_hash: <str> hash of previous Block
        :return: <dict> new Block
        """

        # Create new block
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.utxo,
            'proof': proof,
            'prev_hash': prev_hash
        }

        # Remove recorded transactions from the UTXO
        self.utxo = []

        # Append new Block to the Chain
        self.chain.append(block)
        return block

    def create_new_transaction(self, sender, receiver, amount):
        """
        Create a new Transaction to be added in the next Block

        :param sender: <str> uuid of sender
        :param receiver: <str> uuid of receiver
        :param amount: <int> amount of coins
        :return: <int> index of the Block that will hold this Transaction
        """

        self.utxo.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
        })

        return self.latest_block['index']+1
