"""Configuration module"""

import json
import os


DEFAULT_PORT = 5891

global_config_path = "app-config.json"
current = None


def init():
    global current

    # get environment
    env = os.environ.get('NORIMQ.ENV', 'dev')
    env_config_path = "app-config.{}.json".format(env)

    # read global config
    with open(global_config_path, 'r+') as file:
        current = json.load(file)

    # read environment config
    env_config = {}
    if os.path.exists(env_config_path):
        with open(env_config_path, 'r+') as file_env:
            env_config = json.load(file_env)

    current = {**current, **env_config}


class Storage:
    """Storage configuration"""

    @staticmethod
    def db_path():
        return current['storage']['dbPath']


class Network:
    """Network configuration"""

    @staticmethod
    def port():
        if 'network' in current and 'port' in current['network']:
            return current['network']['port']
        return DEFAULT_PORT
