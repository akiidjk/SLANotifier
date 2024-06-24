import json


def get_config():
    with open('config.json', 'r') as f:
        config = json.load(f)

    logging_level = config['logging_level']
    services = config['services']
    targets = config['targets']
    reload = config['reload']
    save = config['save']

    return logging_level, services, targets, reload, save
