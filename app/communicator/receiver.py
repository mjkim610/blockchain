from socket import *
import json

from app import log
from app import transaction
from app.transaction import Transaction


is_running = True


def stop():
    global is_running
    is_running = False


def start(thread_name, ip_address, port):
    addr = (ip_address, port)
    buf_size = 1024

    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.bind(addr)
    tcp_socket.listen(5)

    while is_running:
        receive_socket, sender_ip = tcp_socket.accept()

        while is_running:
            log.write("Receiving...")
            data=receive_socket.recv(buf_size)

            try:
                if len(data) == 0:
                    break
                data_json_obj = json.loads(data)
                if data_json_obj["type"] == "T":
                    log.write("Receiving a transaction")
                    tx = Transaction().from_json(data_json_obj)
                    transaction.add_transaction(tx)

                elif data_json_obj["type"] == "B":
                    #TODO: validate block
                    #TODO: write block to ledger
                    #TODO: clear transactions
                    pass
            except Exception as e:
                stop()
                print("Exception:", e)
                break

    tcp_socket.close()
    receive_socket.close()