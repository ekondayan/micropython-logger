from micropython import const

from .defs import *
from .handler import LogHandler

class LogConsole(LogHandler):
    _line_format = const('{timestamp} [{level}] {sys}{context} {err_title}{msg}')

    def __init__(self, name: str = 'console', level: int = L_WARNING):
        super().__init__(name, level)

    def send(self, level: int, msg: str, sys = None, context = None, error_id = None, timestamp: tuple = None):
        line = self._prepare_line(level, msg, sys, context, error_id, self._timestamp_format.format(timestamp[0], timestamp[1], timestamp[2],
                                                                                                    timestamp[3], timestamp[4], timestamp[5]))
        if line is not None:
            print(line)