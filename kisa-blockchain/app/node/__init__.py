from app import storage
from sqlalchemy import *

class Node(storage.Base):
    __tablename__ = 'nodes'
    ip_address = Column(String, primary_key=True)
    public_key = Column(String)

    def __init__(self, ip_address):
        self.type = "N"
        self.ip_address = ip_address
        self.public_key = ''

def add_node(node):
    storage.insert_or_update(node, ip_address=node.ip_address)

def get_all():
    return storage.get_all(Node)