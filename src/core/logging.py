"""Logging module"""

import logging


class Logger(logging.getLoggerClass()):
    """Logger class"""

    def __init__(self, name=None):
        if not name:
            name = "System"
        super().__init__(name, level=logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('[{asctime}] {name} {levelname}: {message}', style='{')
        ch.setFormatter(formatter)
        self.addHandler(ch)

