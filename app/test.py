from app.transaction import *

my_tx = create_tx("a", "b", "c")
print(my_tx.message)
print(my_tx.to_json)