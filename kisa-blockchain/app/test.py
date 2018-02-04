from app.transaction import *

tx = create_tx("aa","bb","msg")
print(tx.message)
print(tx.to_json())