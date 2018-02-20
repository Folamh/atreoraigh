import json
import logging
import experiment_handler
from netfilterqueue import NetfilterQueue
from packet_commands import get_payload


def setup_logger():
    log_format = '%(asctime)-15s %(levelname)s: %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)


setup_logger()

netfilter_queue = NetfilterQueue()
experiments = [experiment_handler.ExperimentHandler(56566)]


def manage_packet(packet):
    payload = get_payload(packet)
    logging.info('Packet sent to port: {}'.format(payload.dport))
    for experiment in experiments:
        if payload.dport == experiment.port:
            experiment.manage_packet(packet)


netfilter_queue.bind(1, manage_packet)

try:
    print('[*] waiting for data')
    netfilter_queue.run()
except KeyboardInterrupt:
    pass
