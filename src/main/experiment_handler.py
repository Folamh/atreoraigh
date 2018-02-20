import subprocess
from packet_commands import *


class ExperimentHandler:
    def __init__(self, port):
        self.port = port
        self.experiment = 0
        self.experiment_json = {}
        self.instructions = {}
        self.instruction_counter = 1
        self.route_port()

    def manage_packet(self, packet):
        if self.instructions:
            self.instructions[self.instruction_counter](packet)
            self.instruction_counter += 1
            if self.instruction_counter > len(self.instructions):
                self.instruction_counter = 1
        else:
            logging.info('No instructions for port: {}. Defaulting to accept packet.'.format(self.port))
            accept_packet(packet)

    def route_port(self):
        routing_command = ['sudo', 'iptables', '-A', 'INPUT', '-p', 'udp', '--dport', str(self.port), '-j', 'NFQUEUE',
                           '--queue-num', '1']
        logging.info('Creating new route for port: {}.'.format(self.port))
        logging.debug(routing_command)
        subprocess.Popen(routing_command).communicate()

    def build_instructions(self, experiment_json):
        instructions = {}

        command_map = {
            "ACCEPT": accept_packet,
            "DROP": drop_packet
        }

        for instruction in experiment_json["instructions"]:
            instructions.update({instruction["step"]: command_map[instruction["instruction"]]})

        self.instructions = instructions
