import json
import logging
import socket
import threading
import port_handler, global_vars, iptables


def final_response(client, response):
    response = {
        'type': response
    }
    response = bytes(json.dumps(response), 'utf-8')
    client.sendall(response)


def parse_experiment_instructions(client, data_json):
    add_to_experiments = True
    for experiment in global_vars.experiments:
        if experiment.port == data_json["port"]:
            logging.info('Adding new instructions to experiment.')
            experiment.experiment_json = data_json
            experiment.build_instructions(experiment.experiment_json)
            add_to_experiments = False

    if add_to_experiments:
        logging.info('Adding new experiment.')
        new_instruction_handler = port_handler.PortHandler(int(data_json["port"]), 'INPUT')
        new_instruction_handler.build_instructions(data_json)
        global_vars.experiments.append(new_instruction_handler)

    final_response(client, 'INSTRUCTIONS-OK')


def parse_experiment_record(data_json):
    add_to_experiments = True
    for port in data_json["ports"]:
        for experiment in global_vars.experiments:
            if experiment.port == port["port"]:
                logging.info('Setting port {} to record.'.format(port["port"]))
                experiment.setup_recording()
                add_to_experiments = False

        if add_to_experiments:
            logging.info('Adding new port {} to record.'.format(port["port"]))
            new_instruction_handler = port_handler.PortHandler(int(port["port"]), 'INPUT')
            new_instruction_handler.setup_recording()
            global_vars.experiments.append(new_instruction_handler)


def start_experiments(client, data_json):
    global_vars.current_experiment = data_json["experiment"]
    logging.info('Starting experiment: {}'.format(data_json["experiment"]))
    for experiment in global_vars.experiments:
        experiment.setup_experiment()
    final_response(client, 'START-OK')


def finish_experiment(client):
    logging.info('Experiment finished: Sending lineage to controller')
    for experiment in global_vars.experiments:
        data = json.dumps(experiment.experiment_finished())
        response = bytes(data, 'utf-8')
        client.sendall(response)
    final_response(client, 'FINISH-EXPERIMENT-OK')


def start_recording(client, data_json):
    logging.info('Experiment finished: Sending lineage to controller')
    global_vars.current_experiment = 0
    parse_experiment_record(data_json)
    final_response(client, 'RECORD-OK')


def finish_recording(client):
    logging.info('Recording finished: Sending lineage to controller')
    for experiment in global_vars.experiments:
        data = json.dumps(experiment.recording_finished())
        response = bytes(data, 'utf-8')
        client.sendall(response)
    final_response(client, 'FINISH-RECORD-OK')


def reset_node(client):
    logging.info('Resetting node')
    iptables.reset()
    global_vars.reset()
    final_response(client, 'RESET-OK')


def listen_to_client(client, address):
    size = 4092
    while True:
        try:
            data = client.recv(size)
            received = "Received:{}".format(data)
            data_json = json.loads(data)
            if data:
                logging.info(received)
                if data_json["type"] == "INSTRUCTIONS":
                    parse_experiment_instructions(client, data_json)

                elif data_json["type"] == "START":
                    start_experiments(client, data_json)

                elif data_json["type"] == "FINISH":
                    finish_experiment(client)

                elif data_json["type"] == "RECORD":
                    start_recording(client, data_json)

                elif data_json["type"] == "RECORD-FINISH":
                    finish_recording(client)

                elif data_json["type"] == "RESET":
                    reset_node(client)

                else:
                    raise Exception('Invalid JSON.')
                client.close()
            else:
                raise Exception('Client disconnected')
        except:
            client.close()
            return False


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target=listen_to_client, args=(client, address)).start()


def setup_server():
    HOST, PORT = '0.0.0.0', global_vars.config["PORT"]
    server = ThreadedServer(HOST, PORT)
    threaded_server = threading.Thread(target=server.listen, daemon=True)
    threaded_server.start()
    return server
