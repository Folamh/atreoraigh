import global_vars
import subprocess
import logging
import time


def create_route(type, port, direction):
    routing_command = [direction, '-p', type, '--dport', str(port),
                       '-j', 'NFQUEUE', '--queue-num', '1']
    key = direction + '-' + type + '-' + str(port)
    global_vars.routes.update({key: routing_command})
    logging.debug(routing_command)
    subprocess.Popen(['sudo', 'iptables', '-A'] + routing_command).communicate()


def delete_route(type, port, direction):
    logging.debug('Deleting route for: {}'.format(port))
    key = direction + '-' + type + '-' + str(port)
    if key in global_vars.routes[key]:
        subprocess.Popen(['sudo', 'iptables', '-D'] + global_vars.routes[key])


def reject_route(type, port, direction):
    delete_route(type, port, direction)
    routing_command = [direction, '-p', type, '--dport', str(port),
                       '-j', 'REJECT']
    key = direction + '-' + type + '-' + str(port)
    global_vars.routes.update({key: routing_command})
    logging.debug(routing_command)
    subprocess.Popen(['sudo', 'iptables', '-A'] + routing_command).communicate()
