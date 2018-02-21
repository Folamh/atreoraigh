import logging
import subprocess
from netfilterqueue import NetfilterQueue

import experiment_handler
from packet_commands import get_payload


def setup_logger():
    log_format = '%(asctime)-15s %(levelname)s: %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)


def manage_packet(packet):
    payload = get_payload(packet)
    logging.info('Packet sent to port: {}'.format(payload.dport))
    for experiment in experiments:
        if payload.dport == experiment.port:
            experiment.manage_packet(packet)


if __name__ == '__main__':
    setup_logger()
    server = experiment_handler.setup_server()
    netfilter_queue = NetfilterQueue()
    experiments = []
    netfilter_queue.bind(1, manage_packet)
    try:
        logging.info('[*] waiting for data')
        netfilter_queue.run()
    finally:
        logging.info('Shutting down experiment server...')
        server.shutdown()
        logging.info('Flushing routing tables.')
        flush_command = ['sudo', 'iptables', '-F']
        subprocess.Popen(flush_command).communicate()
        print('Shutting down...')
        exit(0)
