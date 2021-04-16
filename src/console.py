from .defs import *
from .handler import LogHandler

class LogConsole(LogHandler):
    _line_format = '{timestamp} [{level}] {sys}{context} {err_title}{msg}'

    def __init__(self, level = L_WARNING):
        super().__init__('console', level)

    def send(self, level, msg, sys = None, context = None, error_id = None):
        line = self._prepare_line(level, msg, sys, context, error_id)
        if line is not None:
            print(line)