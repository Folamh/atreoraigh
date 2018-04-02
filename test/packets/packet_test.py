from netfilterqueue import NetfilterQueue
import socket


def print_and_accept(pkt):
    print(pkt)
    pkt.accept()


nf_queue = NetfilterQueue()
nf_queue.bind(2, print_and_accept)
s = socket.fromfd(nf_queue.get_fd(), socket.AF_UNIX, socket.SOCK_STREAM)
try:
    nf_queue.run_socket(s)
except KeyboardInterrupt:
    pass

s.close()
nf_queue.unbind()
