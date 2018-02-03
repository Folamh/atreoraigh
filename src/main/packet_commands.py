import logging
import scapy.all as scapy


def drop_packet(packet):
    payload = scapy.IP(packet.get_payload())
    logging.debug('Payload: {}'.format(payload.load))
    logging.info('Dropping packet.')
    packet.drop()


def accept_packet(packet):
    payload = scapy.IP(packet.get_payload())
    logging.debug('Payload: {}'.format(payload.load))
    logging.info('Accepting packet.')
    packet.accept()
