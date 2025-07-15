import os
import json


def analysis_files():
    with os.scandir("rsc") as items:
        paths = [(file.path, file.name) for file in items if file.name.endswith("json")]

    return sorted(paths)


def get_config():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    return config


def set_config(key, value):
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    config[key] = value

    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)
