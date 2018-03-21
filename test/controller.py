import json
import socket


def send_client(port, message):
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.sendto(message.encode('utf-8'), ("", port))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    with open('/home/rmurphy/Projects/atreoraigh/test/sample_instructions.json', 'r') as json_file:
        data = json.load(json_file)
    sock.connect(('', 11211))
    sock.sendall(bytes(json.dumps(data), 'utf-8'))
    response = str(sock.recv(1024), 'utf-8')
    print('{}'.format(response))
    with open('/home/rmurphy/Projects/atreoraigh/test/sample_start_experiment.json', 'r') as json_file:
        data = json.load(json_file)
    sock.sendall(bytes(json.dumps(data), 'utf-8'))
    response = str(sock.recv(1024), 'utf-8')
    print('{}'.format(response))
    for i in range(0, 3):
        send_client(55555, "Test" + str(i))
    sock.close()
