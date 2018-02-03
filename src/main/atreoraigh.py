import json
import logging
from netfilterqueue import NetfilterQueue
from experiment_builder import *

netfilter_queue = NetfilterQueue()


def setup_logger():
    log_format = '%(asctime)-15s %(levelname)s: %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)


setup_logger()

instruction_counter = 0


def manage_packet(packet):
    global instruction_counter

    instructions = build_instructions(json.load(open(
        "/home/rmurphy/Projects/atreoraigh/src/test/sample_instructions.json")))

    instructions[instruction_counter](packet)
    instruction_counter += 1
    if instruction_counter >= len(instructions):
        instruction_counter = 0


netfilter_queue.bind(1, manage_packet)

try:
    print('[*] waiting for data')
    netfilter_queue.run()
except KeyboardInterrupt:
    pass
