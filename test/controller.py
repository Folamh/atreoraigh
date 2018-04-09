import json
import socket
import time
import os
import subprocess


dir_path = os.path.dirname(os.path.realpath(__file__))


def send_client(port, message):
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.sendto(message.encode('utf-8'), ("", port))


def send_json(filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_sock:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        node_sock.connect(('', 11211))
        node_sock.sendall(bytes(json.dumps(data), 'utf-8'))

        while True:
            response = str(node_sock.recv(1024), 'utf-8')
            if response:
                print('Received: {}'.format(response))
            else:
                break
        node_sock.close()

#
print('Recording test:')
send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_start_record.json'))
time.sleep(10)
send_client(55555, "Test0")
time.sleep(3)
send_json(os.path.join(dir_path, 'samples', 'sample_finish_record.json'))
time.sleep(3)

print('\n\nInstructions test:')
send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_instructions0.json'))
time.sleep(3)
send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_instructions1.json'))
time.sleep(3)
send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_instructions2.json'))
time.sleep(3)

print('\n\nExperiment test:')
send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_start_experiment.json'))
time.sleep(3)
send_client(55555, "Test1")
time.sleep(3)
send_json(os.path.join(dir_path, 'samples', 'sample_finish_experiment.json'))
time.sleep(3)

print('\n\nReset test:')
send_json(os.path.join(dir_path, 'samples', 'sample_reset.json'))

# print('\n\nRecording test:')
# send_json(os.path.join(dir_path, 'samples', 'tcp', 'sample_start_record.json'))
# time.sleep(10)
# data = subprocess.Popen(["python", os.path.join(dir_path, 'tcp', 'client.py')])
# time.sleep(5)
# send_json(os.path.join(dir_path, 'samples', 'sample_finish_record.json'))
# time.sleep(3)
