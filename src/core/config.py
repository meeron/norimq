"""Configuration module"""

import json
import os
import logging
from datetime import date


DEFAULT_PORT = 5891
DEFAULT_IP = "0.0.0.0"
DEFAULT_LOGS_DIR = "/var/norimq/logs"

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

    @staticmethod
    def ip():
        if 'network' in current and 'ip' in current['network']:
            return current['network']['ip']
        return DEFAULT_IP


class Logs:
    """Logs configuration"""

    @staticmethod
    def dir_path():
        if 'logs' in current and 'dirPath' in current['logs']:
            return current['logs']['dirPath']
        return DEFAULT_LOGS_DIR

    @staticmethod
    def logfile_path():
        filename = date.today().isoformat() + ".log"
        return os.path.join(Logs.dir_path(), filename)

    @staticmethod
    def min_level():
        level = "INFO"
        if 'logs' in current and 'minLevel' in current['logs']:
            level = current['logs']['minLevel']

        if level == "DEBUG":
            return logging.DEBUG
        if level == "INFO":
            return logging.INFO
        if level == "WARN":
            return logging.WARNING
        if level == "ERROR":
            return logging.ERROR

        return logging.INFO
