import logging
import scapy.all as scapy


def drop_packet(packet):
    payload = get_payload(packet)
    logging.debug('Payload: {}'.format(payload.load))
    logging.info('Dropping packet.')
    packet.drop()


def accept_packet(packet):
    payload = get_payload(packet)
    if payload.getlayer(scapy.Raw):
        logging.debug('Payload: {}'.format(payload.load))
    else:
        logging.debug('No load in packet')
    logging.info('Accepting packet.')
    packet.accept()


def get_payload(packet):
    return scapy.IP(packet.get_payload())