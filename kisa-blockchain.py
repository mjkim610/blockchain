from app import transaction


def exec_menu(choice):
    ch = choice.lower()
    if ch == "":
        menu_actions["main_menu"]()
    else:
        try:
            menu_actions[ch]()
        except Exception as e:
            print("INVALID SELECTION OR ", e)
            menu_actions["main_menu"]()


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


def send_tx():
    print("Input message:")
    message = input(">> ")

    #TODO: get pub_key, pri_key and use them in creating a transaction
    pub_key = ""
    pri_key = ""

    tx = transaction.create_tx(pub_key, pri_key, message)
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
        print("No transaction to show")
    else:
        for t in tx_list:
            log.write(t, logging.DEBUG)
    main_menu()


menu_actions = {
    "main_menu": main_menu,
    "1": send_tx,
    "2": show_node_list,
    "3": show_transaction_list,
    #"4": show_block_list,
    "0": exit,
}

from app import node, communicator, storage
import threading
from app.communicator import receiver

storage.init()
node.add_node(node.Node("192.168.40.10"))
node.add_node(node.Node("192.168.40.11")) # These are static, only for now


listen_thread = threading.Thread(target = receiver.start, args=("LT", "192.168.40.10", 3399))
listen_thread.start()

main_menu()