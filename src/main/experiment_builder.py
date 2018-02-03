from packet_commands import *


def build_instructions(experiment_json):
    instructions = {}

    command_map = {
        "ACCEPT": accept_packet,
        "DROP": drop_packet
    }

    for instruction in experiment_json["instructions"]:
        instructions.update({instruction["step"]: command_map[instruction["instruction"]]})

    return instructions
