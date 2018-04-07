import subprocess

import experiment_handler
from packet_commands import *
import global_vars
import iptables
from datetime import datetime


def route_port(port, direction):
    logging.info('Creating reroute for port: {}.'.format(port))
    iptables.create_route('udp', port, direction)
    iptables.create_route('tcp', port, direction)


def reject_port(port, direction):
    logging.info('Creating rejection route for port: {}.'.format(port))
    iptables.reject_route('udp', port, direction)
    iptables.reject_route('tcp', port, direction)


class InstructionHandler:
    def __init__(self, port, direction):
        self.port = port
        self.direction = direction
        self.experiments_queue = {}
        self.instructions = {}
        self.instruction_counter = 1
        self.lineage = {}
        self.record = False

    def manage_packet(self, packet):
        payload = get_payload(packet)
        if self.record:
            self.lineage_recorder(payload)
            accept_packet(packet)
        elif self.instructions:
            self.lineage_recorder(payload)
            self.instructions[self.instruction_counter](packet)
            if self.instruction_counter > len(self.instructions):
                self.record = True
        else:
            logging.warning(
                'Experiment not started or no instructions for port: {}. '
                'Defaulting to accept packet.'.format(self.port)
            )
            accept_packet(packet)

    def lineage_recorder(self, payload):
        logging.info('Recording packet.')
        self.lineage[global_vars.current_experiment].append({
            datetime.strftime(datetime.utcnow(), '%Y-%m-%d-%H-%M-%S-%f'): {
                'src': payload.src,
                'dst': payload.dst,
                'dport': payload.dport,
                'data': payload.load.decode('utf-8')
            }
        })

    def build_instructions(self, experiment_json):
        instructions = {}

        command_map = {
            'ACCEPT': accept_packet,
            'DROP': drop_packet
        }

        for instruction in experiment_json['instructions']:
            if instruction['instruction'] == 'REJECT':
                logging.debug("REJECT called")
                reject_port(self.port, self.direction)
            else:
                instructions.update({
                    instruction['step']: command_map[instruction['instruction']]
                })

        self.experiments_queue.update({
            experiment_json['experiment']: instructions
        })

    def setup_experiment(self):
        self.record = False
        self.instruction_counter = 1
        self.instructions = self.experiments_queue[global_vars.current_experiment]
        self.lineage.update({global_vars.current_experiment: []})

    def experiment_finished(self):
        logging.info('Instructions for port ' + str(self.port) + ' finished. Lineage: ' + str(self.lineage[global_vars.
                                                                                              current_experiment]))
        self.instructions = {}
        return {'EXPERIMENT' + '-' + str(global_vars.current_experiment) + '-' + str(self.port): self.lineage[
            global_vars.current_experiment]}

    def setup_recording(self):
        self.record = True
        global_vars.current_experiment = 0
        self.lineage.update({global_vars.current_experiment: []})
        route_port(self.port, self.direction)

    def recording_finished(self):
        logging.info('Recording for port ' + str(self.port) + ' finished. Lineage: ' + str(self.lineage))
        self.instructions = {}
        return {'RECORDING' + '-' + str(self.port): self.lineage[0]}

