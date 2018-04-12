dir_path = ''
hostname = ''
config = {}
current_experiment = 0
experiments = []
routes = {}


def reset():
    global config
    global current_experiment
    global experiments
    global routes
    global hostname

    config = {}
    current_experiment = 0
    experiments = []
    routes = {}
