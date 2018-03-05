import json
import logging
import socket
import socketserver
import threading
from time import sleep

import instruction_handler
from atreoraigh import experiments


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):  # TODO Take in multiple types of input.
        data = str(self.request.recv(1024), 'utf-8')
        received = "Received:{}".format(data)
        logging.info(received)
        experiment_json = json.loads(data)
        add_to_experiments = True
        for experiment in experiments:
            if experiment.port == experiment_json["port"]:
                experiment.experiment_json = experiment_json
                experiment.build_instructions(experiment.experiment_json)
                add_to_experiments = False

        if add_to_experiments:
            logging.info('Adding new experiment.')
            experiments.append(instruction_handler.InstructionHandler(int(experiment_json["port"])))
            for experiment in experiments:
                if experiment.port == experiment_json["port"]:
                    experiment.experiment_json = experiment_json
                    logging.info(experiment.experiment_json)
                    experiment.build_instructions(experiment.experiment_json)

        response = bytes(received, 'utf-8')
        print(response)
        self.request.sendall(response)
        self.request.close()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))


def setup_server():
    HOST, PORT = '', 56566
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        # server_thread = threading.Thread(target=server.serve_forever)
        # server_thread.daemon = True
        # server_thread.start()
        server.serve_forever()
    return server
