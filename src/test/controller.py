import json
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    with open('/home/rmurphy/Projects/atreoraigh/src/test/sample_instructions.json', 'r') as json_file:
        data = json.load(json_file)
    sock.connect(('', 56566))
    sock.sendall(bytes(json.dumps(data), 'utf-8'))
    response = str(sock.recv(1024), 'utf-8')
    print('Received: {}'.format(response))
