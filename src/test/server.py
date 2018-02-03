import socket
import sys


def send_msg(ip, port, msg):
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.sendto(msg, (ip, port))


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", int(sys.argv[1])))

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            print("LogServer@Port:" + sys.argv[1] + " Log: " + str(data) + " From: " + addr[0])
            for addr in sys.argv[2:]:
                ip, port = addr.split(":")
                send_msg(ip, int(port), data)
    except KeyboardInterrupt:
        sock.close()
        print("Stopped server")


if __name__ == '__main__':
    main()
