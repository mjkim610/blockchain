from app import storage
from sqlalchemy import *
import datetime
import json
from dateutil import parser

from sqlalchemy import *

from app import storage


class Transaction(storage.Base):
    __tablename__ = 'transaction'
    _id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    time_stamp = Column(DateTime)
    tx_id = Column(String)
    pub_key = Column(String)
    message = Column(String)
    signature = Column(String)

    def __init__(self):
        self.type = 't'
        self.time_stamp = datetime.datetime.now()
        self.tx_id = self.type + self.time_stamp.strftime('%Y%m%d%H%M%S')
        self.pub_key = ''
        self.message = ''
        self.signature = ''

    def to_json(self):
        return json.dumps({
            'type': self.type,
            'time_stamp': self.time_stamp.strftime('%Y%m%d%H%M%S'),
            'tx_id': self.tx_id,
            'pub_key': self.pub_key,
            'message': self.message,
            'signature': self.signature
        })

    def from_json(self, dictionary):
        """Constructor"""
        for key in dictionary:
            setattr(self, key, dictionary[key])

        self.time_stamp = parser.parse(self.time_stamp)
        return self

def add_transaction(tx):
    storage.insert(tx)

def get_transactions():
    return storage.get_all(Transaction)

def create_tx(pub_key, pri_key, msg):
    tx = Transaction()
    tx.pub_key = pub_key
    tx.message = msg

    #TODO need to encrypt tx code

    return tx

def send_tx(tx):
    from app.communicator import sender
    sender.send_to_all_node(tx.to_json)