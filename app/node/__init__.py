import json

from sqlalchemy import Column, String

from app import storage


class Node(storage.Base):
    __tablename__ = 'nodes'

    ip_address = Column(String, primary_key=True)
    type = Column(String)
    pub_key = Column(String)

    def __init__(self, ip_address):
        self.type = "n"
        self.ip_address = ip_address
        self.pub_key = ""

    def __str__(self):
        return self.to_json()

    def to_json(self):
        return json.dumps({
            'type': self.type,
            'ip_address': self.ip_address,
            'pub_key': self.pub_key,
        })


def add_node(node):
    storage.insert_or_update(node, ip_address=node.ip_address)


def get_all():
    return storage.get_all(Node)