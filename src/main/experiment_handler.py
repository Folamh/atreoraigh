import logging
import socketserver
import threading


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):  # TODO Add functionality send experiments to instruction handler.
        data = str(self.request.recv(1024), 'ascii')
        received = "Received: {}".format(data)
        logging.info(received)
        response = bytes(received, 'ascii')
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def setup_server():
    HOST, PORT = 'localhost', 56566
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
    return server
