import sqlite3

# Create a database in RAM
db = sqlite3.connect(':memory:')
# Create or open nodes storage
db = sqlite3.connect('../blockchain.storage')


def create_table():
    db.execute('CREATE TABLE IF NOT EXISTS Nodes(id PRIMARY KEY)')

def add(nodes):
    for node in nodes:
        db.execute('INSERT OR IGNORE INTO Nodes(id) VALUES(?)', [node])
    db.commit()

def read():
    nodes = set()

    nodes_cursor = db.execute('SELECT id FROM Nodes')
    for node in nodes_cursor:
        nodes.add(node[0])

    return nodes

def remove(nodes):
    for node in nodes:
        nodes_cursor = db.execute('SELECT * FROM Nodes WHERE id=?', [node])
        for node2 in nodes_cursor:
            print(node2[0])
    db.commit()

def remove_all():
    db.execute('DELETE FROM Nodes')
    db.commit()