import threading
from socket import *

from app import node

def send(ip_address, message, port, *args):
    receiver_addr = (ip_address, port)
    tcp_socket = socket(AF_INET, SOCK_STREAM)

    try:
        tcp_socket.connect(receiver_addr)
        tcp_socket.send(message.encode("utf-8"))
    except Exception as e:
        print ("Exception at send to :" + ip_address, e)

def send_to_all_node(message):
    address_list = list(map(lambda x: x.ip_address, node.get_all()))

    send_threads = []

    for addr in address_list:
        try:
            t = threading.Thread(target = send, kwargs={"ip_address": addr, "message": message, "port": 3399})
            send_threads.append(t)
        except Exception as e:
            print("Exception (send_to_all_node): ", e)
    for thread in send_threads:
        thread.join()
