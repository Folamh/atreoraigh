import subprocess
from packet_commands import *
from globals import *


class InstructionHandler:
    def __init__(self, port):
        self.port = port
        self.experiments_queue = {}
        self.instructions = {}
        self.instruction_counter = 1
        self.lineage = {}
        self.route_port()

    def manage_packet(self, packet):
        if self.instructions:
            logging.info("Recording packet.")
            self.lineage_recorder(packet)
            self.instructions[self.instruction_counter](packet)
            self.instruction_counter += 1
            if self.instruction_counter > len(self.instructions):
                logging.info("Instructions for port " + str(self.port) + " finished. Lineage: " + str(self.lineage))
                self.instructions = {}

        else:
            logging.warning(
                'Experiment not started or no instructions for port: {}. Defaulting to accept packet.'.format(
                    self.port))
            accept_packet(packet)

    def lineage_recorder(self, packet):
        payload = get_payload(packet)
        self.lineage[current_experiment].append({self.instruction_counter: {
            "src": payload.src,
            "dst": payload.dst,
            "dport": payload.dport,
            "data": payload.load
        }})

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

        self.experiments_queue.update({experiment_json["experiment"]: instructions})

    def setup_experiment(self):
        self.instructions = self.experiments_queue[current_experiment]
        self.lineage.update({current_experiment: []})

    def get_lineage(self):
        return self.lineage
