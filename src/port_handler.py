from packet_commands import accept_packet, drop_packet, get_payload
import global_vars, iptables
from datetime import datetime
import logging
import scapy.all as scapy
import re

proto_values = {
    6: 'TCP',
    17: 'UDP'
}


def route_port(port, direction):
    logging.info('Creating reroute for port: {}.'.format(port))
    iptables.create_route('udp', port, direction)
    iptables.create_route('tcp', port, direction)


def reject_port(port, direction):
    logging.info('Creating rejection route for port: {}.'.format(port))
    iptables.reject_route('udp', port, direction)
    iptables.reject_route('tcp', port, direction)


class PortHandler:
    def __init__(self, port, direction):
        self.port = port
        self.direction = direction
        self.experiments_queue = {}
        self.instructions = {}
        self.instruction_counter = 1
        self.lineage = {}
        self.record = False
        self.reject_return = False

    def manage_packet(self, packet):
        payload = get_payload(packet)
        if proto_values[payload.proto] == 'TCP':
            add_to_experiments = True
            for experiment in global_vars.experiments:
                if experiment.port == payload.sport:
                    if self.reject_return:
                        reject_port(experiment.port, 'OUTPUT')
                    else:
                        self.record = True
                    add_to_experiments = False

            if add_to_experiments:
                logging.info('Adding new experiment.')
                new_instruction_handler = PortHandler(payload.sport, 'OUTPUT')
                if self.reject_return:
                    reject_port(new_instruction_handler.port, 'OUTPUT')
                else:
                    new_instruction_handler.setup_recording()
                global_vars.experiments.append(new_instruction_handler)

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
        if payload.getlayer(scapy.Raw):
            logging.info('Recording packet.')

            encoding = 'utf-8'
            decoded_payload = re.sub(r'[^ -~]', '', payload.load.decode(encoding, 'ignore'))

            lineage = {
                datetime.strftime(datetime.utcnow(), '%Y-%m-%d-%H-%M-%S-%f'): {
                    'host': global_vars.hostname,
                    'direction': self.direction,
                    'src': payload.src,
                    'sport': payload.sport,
                    'dst': payload.dst,
                    'dport': payload.dport,
                    'type': proto_values[payload.proto],
                    'data': decoded_payload
                }
            }
            logging.debug('Lineage: {}'.format(lineage))
            self.lineage[global_vars.current_experiment].append(lineage)

    def build_instructions(self, experiment_json):
        instructions = {}

        command_map = {
            'ACCEPT': accept_packet,
            'DROP': drop_packet
        }

        for instruction in experiment_json['instructions']:
            if instruction['instruction'] == 'REJECT':
                reject_port(self.port, self.direction)
            elif instruction['instruction'] == 'REJECT-RETURN':
                self.reject_return = True
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
        logging.info('Instructions for port {} finished. Lineage: {}'
                     .format(self.port, self.lineage[global_vars.current_experiment]))
        self.instructions = {}
        return {'EXPERIMENT-{}'.format(global_vars.current_experiment): self.lineage[global_vars.current_experiment]}

    def setup_recording(self):
        self.record = True
        self.lineage.update({global_vars.current_experiment: []})
        route_port(self.port, self.direction)

    def recording_finished(self):
        logging.info('Recording for port {} finished. Lineage: {}'.format(self.port, self.lineage))
        lineage = {'RECORDING': self.lineage[0]}
        logging.debug('Sending: {}'.format(lineage))
        return lineage

