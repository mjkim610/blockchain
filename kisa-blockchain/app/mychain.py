def show_block_list():
    print("Block list")

def send_tx():
    from app import transaction

    print("Input message")
    choice = input(">> ")

    # TODO pri_key, pub_key
    pri_key = ""
    pub_key = ""
    tx = transaction.create_tx(pub_key, pri_key, choice)
    transaction.send_tx(tx)
    main_menu()

    return


def show_node_list():
    from app import node, log
    import logging
    for n in node.get_all():
        log.write(n, logging.DEBUG)
    main_menu()


def show_transaction_list():
    from app import transaction, log
    import logging
    tx_list = transaction.get_transactions()
    if len(tx_list) == 0:
        print("No Transaction")
        main_menu
    else :
        for t in tx_list:
            log.write(t.message, logging.DEBUG)
        main_menu()

def main_menu():
    print("\nPlease choose the menu:")
    print("1. Send a transaction")
    print("2. Show node list")
    print("3. Show transaction list")
    print("4. Show block list")

    print("0. Quit")
    choice = input(">> ")
    exec_menu(choice)
    return

def exec_menu(choice):
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except:
            print("Invalid selection")
            menu_actions['main_menu']()


menu_actions={
    'main_menu' : main_menu,
    '1': send_tx,
    '2': show_node_list,
    '3': show_transaction_list,
    '4': show_block_list,
    '0': exit,
}

from app import node,storage, transaction
import threading
from app.communicator import receiver

storage.init()
node.add_node(node.Node("192.168.40.169"))
node.add_node(node.Node("192.168.40.17"))
node.add_node(node.Node("192.168.40.6"))
#transaction.add_transaction(transaction.create_tx("","","aaa"))
listen_thread = threading.Thread(target = receiver.start, args=("LT","192.168.40.169",3399))
listen_thread.start()
main_menu()
