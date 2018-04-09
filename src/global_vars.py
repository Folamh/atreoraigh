dir_path = ''
name = ''
config = {}
current_experiment = 0
experiments = []
routes = {}


def reset():
    global config
    global current_experiment
    global experiments
    global routes
    global name

    config = {}
    current_experiment = 0
    experiments = []
    routes = {}
