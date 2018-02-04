from socket import *

is_running = True

def stop():
    global is_running
    is_running = False

def start(thread_name, ip_address, port):
    from app import log

    addr = (ip_address,port)
    buf_size = 1024

    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.bind(addr)
    tcp_socket.listen(5)

    while is_running:

        receive_socket, sender_ip = tcp_socket.accept()
        while is_running:
            log.write("Receiving")
            data=receive_socket.recv(buf_size)
            try:
                import json
                if len(data) == 0:
                    break
                data_json_obj = json.loads(data)
                if data_json_obj['type'] == 't':
                    from app.transaction import Transaction
                    from app import transaction

                    log.write("Receiving a transaction")
                    tx = Transaction().from_json(data_json_obj)
                    transaction.add_transaction(tx)

                elif data_json_obj['type'] == 'b':
                    log.write("Block received")
                    #TODO validate block
                    #TODO add block to ledger
                    #TODO clear transaction
            except:
                import traceback
                traceback.print_exc()
                break
    tcp_socket.close()
    receive_socket.close()