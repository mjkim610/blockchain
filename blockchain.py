class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.utxo = []

    @property
    def latest_block(self):
        pass

    @staticmethod
    def calculate_hash(block):
        pass

    def create_new_block(self):
        pass

    def create_new_transaction(self):
        pass

