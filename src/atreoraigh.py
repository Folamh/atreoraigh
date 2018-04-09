import json
import logging
from netfilterqueue import NetfilterQueue
import experiment_handler, global_vars, iptables
from packet_commands import get_payload
import os
import subprocess

global_vars.dir_path = os.path.dirname(os.path.realpath(__file__))


def read_config():
    with open(os.path.join(global_vars.dir_path, 'configs', 'config.json')) as json_data:
        global_vars.config = json.load(json_data)

    global_vars.config["HOST"] = subprocess.Popen(['hostname', '-I']).communicate()
    print(global_vars.config["HOST"])


def setup_logger():
    log_format = '%(asctime)-15s %(levelname)s: %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)


def manage_packet(packet):
    payload = get_payload(packet)
    logging.info('Packet sent to port: {}'.format(payload.dport))
    for experiment in global_vars.experiments:
        if payload.dport == experiment.port:
            experiment.manage_packet(packet)


def shutdown():
    iptables.reset()
    print('Shutting down...')
    exit(0)


if __name__ == '__main__':
    read_config()
    setup_logger()
    server = experiment_handler.setup_server()
    netfilter_queue = NetfilterQueue()
    netfilter_queue.bind(1, manage_packet)
    try:
        logging.info('[*] waiting for data')
        netfilter_queue.run()
    finally:
        shutdown()
