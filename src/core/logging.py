"""Logging module"""

import logging
from os import path
from src.core import config


class Logger(logging.getLoggerClass()):
    """Logger class"""

    def __init__(self, name=None):
        if not name:
            name = "System"
        super().__init__(name, level=logging.INFO)
        self.addHandler(_create_handler('ch'))

        fh = _create_handler('fh')
        if fh:
            self.addHandler(fh)


def _create_formatter():
    return logging.Formatter('[{asctime}] {name} {levelname}: {message}', style='{')


def _create_handler(h_type):
    handler = None

    if h_type == 'ch':
        handler = logging.StreamHandler()
    if h_type == 'fh' and path.isdir(config.Logs.dir_path()):
        handler = logging.FileHandler(filename=config.Logs.logfile_path())

    if not handler:
        return None

    handler.setFormatter(_create_formatter())

    return handler
