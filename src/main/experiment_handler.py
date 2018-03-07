import json
import logging
import socket
import threading

import instruction_handler
import globals


def experiment_instructions(data_json):
    add_to_experiments = True
    for experiment in globals.experiments:
        if experiment.port == data_json["port"]:
            logging.info('Adding new instructions to experiment.')
            experiment.experiment_json = data_json
            experiment.build_instructions(experiment.experiment_json)
            add_to_experiments = False

    if add_to_experiments:
        logging.info('Adding new experiment.')
        globals.experiments.append(instruction_handler.InstructionHandler(int(data_json["port"])))
        logging.debug(globals.experiments)
        for experiment in globals.experiments:
            if experiment.port == data_json["port"]:
                experiment.build_instructions(data_json)


def start_experiment(data_json):
    globals.current_experiment = data_json["experiment"]
    for experiment in globals.experiments:
        experiment.setup_experiment()


def listen_to_client(client, address):
    size = 1024
    while True:
        try:
            data = client.recv(size)
            received = "Received:{}".format(data)
            logging.info(received)
            data_json = json.loads(data)
            if data:
                if data_json["type"] == "INSTRUCTIONS":
                    experiment_instructions(data_json)
                    response = bytes(received, 'utf-8')
                    client.send(response)
                elif data_json["type"] == "START":
                    start_experiment(data_json)
                    response = bytes(received, 'utf-8')
                    client.send(response)
                # TODO Add a record start and finish
                else:
                    raise Exception('Invalid JSON.')
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
    HOST, PORT = '', 56565
    server = ThreadedServer(HOST, PORT)
    threaded_server = threading.Thread(target=server.listen, daemon=True)
    threaded_server.start()
    return server
