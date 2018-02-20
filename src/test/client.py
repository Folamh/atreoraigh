import socket
import sys

def main():
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.sendto(sys.argv[2].encode('utf-8'), ("", int(sys.argv[1])))


if __name__ == '__main__':
    main()
