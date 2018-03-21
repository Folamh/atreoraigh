import subprocess

import experiment_handler
from packet_commands import *
import global_vars


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
                experiment_handler.send_lineage(
                    {global_vars.current_experiment: self.lineage[global_vars.current_experiment]})
                self.instructions = {}
                self.instruction_counter = 1

        else:
            logging.warning(
                'Experiment not started or no instructions for port: {}. Defaulting to accept packet.'.format(
                    self.port))
            accept_packet(packet)

    # TODO Add a record start and finish

    def lineage_recorder(self, packet):
        payload = get_payload(packet)
        self.lineage[global_vars.current_experiment].append({self.instruction_counter: {
            "src": payload.src,
            "dst": payload.dst,
            "dport": payload.dport,
            "data": payload.load.decode("utf-8")
        }})

    def route_port(self):
        logging.info('Creating new route for port: {}.'.format(self.port))

        def route(type):
            routing_command = ['sudo', 'iptables', '-A', 'INPUT', '-p', type, '--dport', str(self.port), '-j',
                               'NFQUEUE',
                               '--queue-num', '1']
            logging.debug(routing_command)
            subprocess.Popen(routing_command).communicate()

        route('udp')
        route('tcp')

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
        self.instructions = self.experiments_queue[global_vars.current_experiment]
        self.lineage.update({global_vars.current_experiment: []})
