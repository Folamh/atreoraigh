import json
import logging
import socket
import threading
import instruction_handler
import global_vars


def experiment_instructions(data_json):
    add_to_experiments = True
    for experiment in global_vars.experiments:
        if experiment.port == data_json["port"]:
            logging.info('Adding new instructions to experiment.')
            experiment.experiment_json = data_json
            experiment.build_instructions(experiment.experiment_json)
            add_to_experiments = False

    if add_to_experiments:
        logging.info('Adding new experiment.')
        new_instruction_handler = instruction_handler.InstructionHandler(int(data_json["port"]), 'INPUT')
        new_instruction_handler.build_instructions(data_json)
        global_vars.experiments.append(new_instruction_handler)


def experiment_record(data_json):
    add_to_experiments = True
    for port in data_json["ports"]:
        for experiment in global_vars.experiments:
            if experiment.port == port["port"]:
                logging.info('Setting port {} to record.'.format(port["port"]))
                experiment.setup_recording()
                add_to_experiments = False

        if add_to_experiments:
            logging.info('Adding new port {} to record.'.format(port["port"]))
            new_instruction_handler = instruction_handler.InstructionHandler(int(port["port"]), 'INPUT')
            new_instruction_handler.setup_recording()
            global_vars.experiments.append(new_instruction_handler)


def start_experiment(data_json):
    global_vars.current_experiment = data_json["experiment"]
    logging.info('Starting experiment: ' + str(global_vars.current_experiment))
    for experiment in global_vars.experiments:
        experiment.setup_experiment()


def listen_to_client(client, address):
    size = 1024
    while True:
        try:
            data = client.recv(size)
            received = "Received:{}".format(data)
            data_json = json.loads(data)
            if data:
                logging.info(received)
                if data_json["type"] == "INSTRUCTIONS":
                    experiment_instructions(data_json)
                    response = bytes('INSTRUCTIONS', 'utf-8')
                    client.sendall(response)

                elif data_json["type"] == "START":
                    start_experiment(data_json)
                    response = bytes('START', 'utf-8')
                    client.sendall(response)

                elif data_json["type"] == "FINISH":
                    logging.info('Sending lineage to controller')
                    for experiment in global_vars.experiments:
                        data = json.dumps(experiment.experiment_finished())
                        response = bytes(data, 'utf-8')
                        client.sendall(response)

                elif data_json["type"] == "RECORD":
                    experiment_record(data_json)
                    response = bytes('RECORD', 'utf-8')
                    client.sendall(response)

                elif data_json["type"] == "RECORD-FINISH":
                    logging.info('Sending lineage to controller')
                    for experiment in global_vars.experiments:
                        data = json.dumps(experiment.recording_finished())
                        response = bytes(data, 'utf-8')
                        client.sendall(response)
                elif data_json["type"] == "RESET":
                    logging.info('Resetting node.')
                    global_vars.reset()
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
    HOST, PORT = global_vars.config["HOST"], global_vars.config["PORT"]
    server = ThreadedServer(HOST, PORT)
    threaded_server = threading.Thread(target=server.listen, daemon=True)
    threaded_server.start()
    return server
