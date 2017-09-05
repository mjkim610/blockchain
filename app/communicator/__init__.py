import socket
import threading
import time
import zmq

from app import node

PING_PORT_NUMBER = 3366
PING_MSG_SIZE = 1
PING_INTERVAL = 5 # once per second

def start():

    def find_node_thread():
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_UDP)
        # Ask operating system to let us do broadcasts from socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Bind UDP socket to local port so we can receive pings
        sock.bind("", PING_PORT_NUMBER)

        # main ping loop
        # We use zmq_poll to wait for activity on the UDP socket, since
        # this function works on non-0MQ file handles. We send a beacon
        # once a second, and we collect and report beacons that come in
        # from other nodes:
        poller = zmq.Poller()
        poller.register(sock, zmq.POLLIN)

        ping_at = time.time()

        while True:
            timeout = ping_at - time.time()
            if timeout < 0:
                timeout = 0
            try:
                events = dict(poller.poll(1000 * timeout))
            except KeyboardInterrupt:
                print("Interrupted")
                break

            # Someone answered our ping
            if sock.fileno() in events:
                msg, addrinfo = sock.recvfrom(PING_MSG_SIZE)
                ip = addrinfo[0]
                n = node.Node(ip)
                if node.add_node(n):
                    print("Found " + ip)

            if time.time() >= ping_at:
                print("Finding a node...")
                sock.sendto(b'!', 0, ("255.255.255.255", PING_PORT_NUMBER))
                ping_at = time.time() + PING_INTERVAL

    threading.Thread(target = find_node_thread()).start()

#TODO (personal): if a node doesn't respond to a ping, delete it from the network