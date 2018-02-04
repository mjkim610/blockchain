import hashlib
import json
from argparse import ArgumentParser
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


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

    @staticmethod
    def is_valid_proof(prev_proof, proof):
        """
        Validate the proof

        :param prev_proof: <int> previous Proof
        :param proof: <current Proof
        :return: <bool>
        """

        guess = f'{prev_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

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

    def get_proof(self, prev_proof):
        """
        Perform the Proof of Work algorithm
            - Find a number p' such that hash(pp') contains 4 leading zeroes
            - p is the previous Proof, p' is the current Proof

        :param prev_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.is_valid_proof(prev_proof, proof) is False:
            proof += 1

        return proof


# Instantiate Node
app = Flask(__name__)

# Generate a uuid for this Node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():

    # Get Proof for next new Block
    latest_block = blockchain.latest_block
    latest_proof = latest_block['proof']
    proof = blockchain.get_proof(latest_proof)

    # Use dummy sender with id `miner_reward` for mined coin
    blockchain.create_new_transaction(
        sender="miner_reward",
        receiver=node_identifier,
        amount=1,
    )

    # Create new Block and add to Chain
    latest_hash = blockchain.calculate_hash(latest_block)
    new_block = blockchain.create_new_block(proof, latest_hash)

    response = {
        'message': "New Block created",
        'index': new_block['index'],
        'transactions': new_block['transactions'],
        'proof': new_block['proof'],
        'prev_hash': new_block['prev_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/create', methods=['POST'])
def create_transaction():

    values = request.get_json()

    # Check that the required fields are in the POST data
    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.create_new_transaction(
        sender=values['sender'],
        receiver=values['receiver'],
        amount=values['amount'],
    )

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain/get', methods=['GET'])
def get_chain():

    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain,
    }
    return jsonify(response), 200


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port number for web app')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
