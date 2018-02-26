import hashlib
import json
from argparse import ArgumentParser
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

import db


class Blockchain(object):
    def __init__(self):
        # Create database tables
        db.create_table_nodes()

        # Initialize Blockchain elements
        self.chain = []
        self.utxo = []
        self.nodes = db.read_nodes()

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

    def is_valid_chain(self, chain):
        """
        Validate a chain

        :param chain: <list> a chain
        :return: <bool>
        """

        cur_index = 1

        while cur_index < len(chain):
            prev_block = chain[cur_index-1]
            cur_block = chain[cur_index]
            print(f'{prev_block}')
            print(f'{cur_block}')
            print("\n---------\n")

            # Check that the hash of the Block is correct
            if cur_block['prev_hash'] != self.calculate_hash(prev_block):
                return False

            # Check that the Proof is correct
            if not self.is_valid_proof(prev_block['proof'], cur_block['proof']):
                return False

            cur_index += 1

        return True

    def register_node(self, address):
        """
        Add a new Node to the list

        :param address: <str> address of Node (eg. 'http://192.168.0.1:5000')
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        db.add_nodes(self.nodes)

    def deregister_node(self, address):
        """
        Remove a Node from the list

        :param address: <str> address of Node (eg. 'http://192.168.0.1:5000')
        :return: None
        """

        parsed_url = urlparse(address)
        if (self.nodes.discard(parsed_url.netloc)):
            db.remove_nodes(parsed_url.netloc)

    def deregister_all_nodes(self):
        """
        Remove all Nodes from the list

        :return: None
        """

        self.nodes = set()
        db.remove_all_nodes()

    def resolve_conflicts(self):
        """
        Perform the Consensus algorithm
        If there is a conflict, replace current Chain with the longest Chain in the network


        :return: <bool> True if chain was replaced
        """

        new_chain = None
        max_length = len(self.chain)

        # Verify all the Chains in the network
        for node in self.nodes:
            response = requests.get(f'http://{node}/chain/get')

            if response.status_code == 200:
                cur_length = response.json()['length']
                cur_chain = response.json()['chain']

                # Check if length of Chain is longer and is valid
                if cur_length > max_length and self.is_valid_chain(cur_chain):
                    max_length = cur_length
                    new_chain = cur_chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

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


@app.route('/nodes/register', methods=['POST'])
def register_nodes():

    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please provide a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': "New Nodes have been added",
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/deregister', methods=['POST'])
def deregister_nodes():

    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please provide a valid list of nodes", 400

    for node in nodes:
        blockchain.deregister_node(node)

    response = {
        'message': "Nodes have been removed",
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 200


@app.route('/nodes/deregister-all', methods=['POST'])
def deregister_all_nodes():

    blockchain.deregister_all_nodes()

    response = {
        'message': "All Nodes have been removed",
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 200


@app.route('/nodes/resolve', methods=['GET'])
def resolve_conflicts():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': "This node\'s chain has been replaced",
            'new_chain': blockchain.chain,
        }
    else:
        response = {
            'message': "This node\'s chain is authoritative",
            'chain': blockchain.chain,
        }

    return jsonify(response), 200


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port number for web app')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
