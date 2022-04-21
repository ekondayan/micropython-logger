import uos

from .defs import *
from .handler import LogHandler

class LogFile(LogHandler):
    _line_format = '{timestamp} [{level}] {sys}{context} {err_title}{msg}'

    def __init__(self, name: str, level: int = L_WARNING, file_path: str = '/', file_size_limit: int = 4096, file_count: int = 3):
        if not isinstance(file_count, int) or not 1 <= file_count <= 99:
            raise ValueError('Invalid parameter: file_count={} must be in range 1-99'.format(file_count))
        elif not isinstance(file_size_limit, int) or not file_count > 0:
            raise ValueError('Invalid parameter: file_size_limit={} must be greater than 0'.format(file_size_limit))

        super().__init__(name, level)

        self._file_size_limit = file_size_limit
        self._file_count = file_count

        self._file_full_path = '{}/{}.log'.format(file_path.rstrip('/'), name)
        self._file = open(self._file_full_path, 'at')

    def __del__(self):
        self._file.close()

    def send(self, level: int, msg: str, sys = None, context = None, error_id = None, timestamp: tuple = None):
        try:
            uos.stat(self._file_full_path)
        except OSError:
            self._file = open(self._file_full_path, 'at')

        line = self._prepare_line(level, msg, sys, context, error_id, self._timestamp_format.format(timestamp[0], timestamp[1], timestamp[2],
                                                                                                    timestamp[3], timestamp[4], timestamp[5]))
        if line is not None:
            print(line, file = self._file)
            self._file.flush()
            size = uos.stat(self._file_full_path)[6]
            if size > self._file_size_limit:
                self.log_rotate()

    def log_rotate(self):
        for i in range(self._file_count - 1, 0, -1):
            old_filename = '{}.{}'.format(self._file_full_path, i)
            new_filename = '{}.{}'.format(self._file_full_path, i + 1)
            try:
                uos.rename(old_filename, new_filename)
            except:
                pass

        try:
            uos.remove('{}.{}'.format(self._file_full_path, self._file_count))
        except:
            pass

        self._file.close()
        uos.rename(self._file_full_path, self._file_full_path + '.1')

        self._file = open(self._file_full_path, 'at')

    def delete_logs(self):
        try:
            uos.remove(self._file_full_path)
        except:
            pass

        for i in range(1, self._file_count):
            try:
                uos.remove('{}.{}'.format(self._file_full_path, i))
            except:
                pass
