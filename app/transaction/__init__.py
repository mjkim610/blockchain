import datetime
import json
from app.communicator import sender

from sqlalchemy import Column, String, Integer, DateTime

from app import storage


class Transaction(storage.Base):
    __tablename__ = "transactions"

    _id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    time_stamp = Column(DateTime)
    tx_id = Column(String)
    pub_key = Column(String)
    message = Column(String)
    signature = Column(String)


    def __init__(self):
        self.type = "T"
        self.time_stamp = datetime.datetime.now()
        self.tx_id = self.type + self.time_stamp.strftime("%Y%m%d%H%M%S")
        self.pub_key = ""
        self.message = ""
        self.signature = ""


    def to_json(self):
        return json.dumps({
            'type': self.type,
            'time_stamp': self.time_stamp.strftime("%Y%m%d%H%M%S"),
            'tx_id': self.tx_id,
            'pub_key': self.pub_key,
            'message': self.message,
            'signature': self.signature
        })


def add_transaction(tx):
    storage.init(tx)


def get_transactions():
    storage.get_all(Transaction)


def create_tx(pub_key, pri_key, msg):
    tx = Transaction()
    tx.message = msg

    tx.pub_key = pub_key
    #TODO: encrypt tx code

    return tx


def send_tx(tx):
    sender.send_to_all_nodes(tx.to_json)
    #TODO: create sender package