import subprocess

import experiment_handler
from packet_commands import *
import global_vars
import iptables


class InstructionHandler:
    def __init__(self, port):
        self.port = port
        self.experiments_queue = {}
        self.instructions = {}
        self.instruction_counter = 1
        self.lineage = {}

    def manage_packet(self, packet):
        if self.instructions:
            logging.info('Recording packet.')
            payload = get_payload(packet)

            self.lineage_recorder(payload)

            self.instructions[self.instruction_counter](packet)

            self.instruction_counter += 1
            if self.instruction_counter > len(self.instructions):
                logging.info('Instructions for port ' + str(self.port) + ' finished. Lineage: ' + str(self.lineage))
                experiment_handler.send_lineage(
                    {global_vars.current_experiment: self.lineage[global_vars.current_experiment]})
                self.instructions = {}
                self.instruction_counter = 1
        else:
            logging.warning(
                'Experiment not started or no instructions for port: {}. Defaulting to accept packet.'.format(
                    self.port))
            accept_packet(packet)

    def route_port(self, direction):
        logging.info('Creating reroute for port: {}.'.format(self.port))
        iptables.create_route('udp', self.port, direction)
        iptables.create_route('tcp', self.port, direction)

    def reject_port(self):
        logging.info('Creating rejection route for port: {}.'.format(port))
        iptables.reject_route('udp', self.port, direction)
        iptables.reject_route('tcp', self.port, direction)

    def lineage_recorder(self, payload):
        self.lineage[global_vars.current_experiment].append({self.instruction_counter: {
            'src': payload.src,
            'dst': payload.dst,
            'dport': payload.dport,
            'data': payload.load.decode('utf-8')
        }})

    def build_instructions(self, experiment_json):
        instructions = {}

        command_map = {
            'ACCEPT': accept_packet,
            'DROP': drop_packet
        }

        for instruction in experiment_json['instructions']:
            if instruction['instruction'] == 'REJECT':
                self.reject_port()
            else:
                instructions.update({instruction['step']: command_map[instruction['instruction']]})

        self.experiments_queue.update({experiment_json['experiment']: instructions})

    def setup_experiment(self):
        self.instructions = self.experiments_queue[global_vars.current_experiment]
        self.lineage.update({global_vars.current_experiment: []})
