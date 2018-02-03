import logging
import scapy.all as scapy


def drop_packet(packet):
    logging.info('Dropping packet.')
    packet.drop()


def accept_packet(packet):
    payload = scapy.IP(packet.get_payload())
    logging.info('Accepting packet.')
    logging.debug('Payload: {}'.format(payload.load))
    packet.accept()
