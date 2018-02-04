import threading, socket, time
import zmq
from app import log
from app import node

PING_PORT_NUMBER = 3366
PING_MSG_SIZE = 1
PING_INTERVAL = 5
is_running = True

def start():
    def find_node_thread():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind('', PING_PORT_NUMBER)

        poller = zmq.Poller()
        poller.register(sock, zmq.POLLIN)

        ping_at = time.time()

        while is_running:
            timeout = ping_at - time.time()
            if timeout < 0:
                timeout = 0

            try:
                events = dict(poller.pool(1000*timeout))
            except KeyboardInterrupt:
                log.write("interrupted")
                break

            if sock.fileno() in events:
                msg, addrinfo = sock.recvfrom(PING_MSG_SIZE)
                ip = addrinfo[0]
                n = node.Node(ip)
                if node.add_node(n):
                    log.write('Find '+ ip)

            if time.time() >= ping_at:
                sock.sendto(b'!', 0, ("255.255.255.255", PING_PORT_NUMBER))
                ping_at = time.time() + PING_INTERVAL


    t = threading.Thread(target = find_node_thread)
    t.start()