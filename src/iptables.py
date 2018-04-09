from src import global_vars
import subprocess
import logging


def delete_route(type, port, direction):
    key = direction + '-' + type + '-' + str(port)
    if global_vars.routes.get(key, None):
        logging.debug('Deleting rule: {}'.format(key))
        subprocess.Popen(['sudo', 'iptables', '-D'] + global_vars.routes[key]).communicate()


def create_route(type, port, direction):
    delete_route(type, port, direction)
    routing_command = [direction, '-p', type, '--dport', str(port),
                       '-j', 'NFQUEUE', '--queue-num', '1']
    key = direction + '-' + type + '-' + str(port)
    global_vars.routes.update({key: routing_command})
    logging.debug(routing_command)
    subprocess.Popen(['sudo', 'iptables', '-A'] + routing_command).communicate()


def reject_route(type, port, direction):
    delete_route(type, port, direction)
    routing_command = [direction, '-p', type, '--dport', str(port),
                       '-j', 'REJECT']
    key = direction + '-' + type + '-' + str(port)
    global_vars.routes.update({key: routing_command})
    logging.debug(routing_command)
    subprocess.Popen(['sudo', 'iptables', '-A'] + routing_command).communicate()


def reset():
    logging.info('Flushing routing tables.')
    for key in global_vars.routes:
        logging.debug('Deleting rule: {}'.format(key))
        subprocess.Popen(['sudo', 'iptables', '-D'] + global_vars.routes[key]).communicate()
