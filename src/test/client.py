import socket
import sys

def main():
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.sendto(sys.argv[1].encode('utf-8'), ("", 56565))


if __name__ == '__main__':
    main()
