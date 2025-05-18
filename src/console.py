from .defs import L_WARNING
from .handler import LogHandler


class LogConsole(LogHandler):
    _line_format = '{timestamp} [{level}] {sys}{context} {err_title}{msg}'

    def __init__(self, name: str = 'console', level: int = L_WARNING, print_errors: bool = False):
        super().__init__(name, level, print_errors)

    def send(self, level: int, msg: str, sys = None, context = None, error_id = None, timestamp: tuple = None):
        line = self._prepare_line(level, msg, sys, context, error_id, self._format_timestamp_tuple(timestamp))

        if line is not None:
            print(line)
