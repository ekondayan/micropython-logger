from .defs import *
from .handler import LogHandler

class LogFile(LogHandler):
    _line_format = '{timestamp} [{level}] {sys}{context} {err_title}{msg}'

    def __init__(self, name, level = L_WARNING, path: str = '/', max_size: int = 20480):
        super().__init__(name, level)

        self._file_path = '{}/{}.log'.format(path.rstrip('/'), name)
        self._max_size = max_size
        self._file = open(self._file_path, 'at')

    def __del__(self):
        self._file.close()

    def send(self, level, msg, sys = None, context = None, error_id = None):
        line = self._prepare_line(level, msg, sys, context, error_id)
        if line is not None:
            print(line, file = self._file)
            self._file.flush()

    def log_rotate(self):
        pass

    def log_reset(self):
        pass