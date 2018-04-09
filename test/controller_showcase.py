import json
import socket
import time
import os
import subprocess


dir_path = os.path.dirname(os.path.realpath(__file__))


def send_json(host, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_sock:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        node_sock.connect((host, 11211))
        node_sock.sendall(bytes(json.dumps(data), 'utf-8'))

        while True:
            response = str(node_sock.recv(1024), 'utf-8')
            if response:
                print('Received: {}'.format(response))
            else:
                break
        node_sock.close()


hosts = {
    'program': 'ec2-52-51-178-23.eu-west-1.compute.amazonaws.com',
    'database1': 'ec2-34-245-55-36.eu-west-1.compute.amazonaws.com',
    'database2': 'ec2-34-240-224-218.eu-west-1.compute.amazonaws.com'
}

print('Recording test:')
send_json(hosts['program'], os.path.join(dir_path, 'samples', 'showcase', 'sample_start_record-program.json'))
send_json(hosts['database1'], os.path.join(dir_path, 'samples', 'showcase', 'sample_start_record-database.json'))
send_json(hosts['database2'], os.path.join(dir_path, 'samples', 'showcase', 'sample_start_record-database.json'))
input('Continue... ')
for host in hosts:
    send_json(hosts[host], os.path.join(dir_path, 'samples', 'sample_finish_record.json'))
# time.sleep(3)
#
# print('\n\nInstructions test:')
# send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_instructions0.json'))
# time.sleep(3)
# send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_instructions1.json'))
# time.sleep(3)
# send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_instructions2.json'))
# time.sleep(3)
#
# print('\n\nExperiment test:')
# send_json(os.path.join(dir_path, 'samples', 'udp', 'sample_start_experiment.json'))
# time.sleep(3)
# time.sleep(3)
# send_json(os.path.join(dir_path, 'samples', 'sample_finish_experiment.json'))
# time.sleep(3)
#
# print('\n\nReset test:')
# send_json(os.path.join(dir_path, 'samples', 'sample_reset.json'))
#
# print('\n\nRecording test:')
# send_json(os.path.join(dir_path, 'samples', 'tcp', 'sample_start_record.json'))
# time.sleep(10)
# data = subprocess.Popen(["python", os.path.join(dir_path, 'tcp', 'client.py')])
# time.sleep(5)
# send_json(os.path.join(dir_path, 'samples', 'sample_finish_record.json'))
# time.sleep(3)
