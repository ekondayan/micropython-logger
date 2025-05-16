import os
from micropython import const

from .defs import L_WARNING
from .handler import LogHandler


class LogFile(LogHandler):
    _line_format = const('{timestamp} [{level}] {sys}{context} {err_title}{msg}')

    def __init__(self, name: str, level: int = L_WARNING, file_path: str = '/', file_size_limit: int = 4096, file_count: int = 3, print_errors: bool = False):
        if not isinstance(file_count, int) or not 1 <= file_count <= 99:
            raise ValueError(f'Invalid parameter: file_count={file_count} must be in range 1-99')
        elif not isinstance(file_size_limit, int) or not file_size_limit > 0:
            raise ValueError(f'Invalid parameter: file_size_limit={file_size_limit} must be greater than 0')

        # Validate name doesn't contain path separators or traversal sequences
        if '/' in name or '\\' in name or '..' in name:
            raise ValueError(f'Invalid parameter: name "{name}" cannot contain path separators or ".."')

        super().__init__(name, level, print_errors)

        self._file_size_limit = file_size_limit
        self._file_count = file_count

        # More efficient path building
        self._file_full_path = file_path.rstrip('/') + '/' + name + '.log'
        self._file = open(self._file_full_path, 'at')

    def __del__(self):
        if hasattr(self, '_file') and self._file:
            try:
                self._file.close()
            except Exception as e:
                if self._print_errors:
                    print(f"LogFile[{self.name}]: Failed to close file: {e}")

    def send(self, level: int, msg: str, sys = None, context = None, error_id = None, timestamp: tuple = None):
        try:
            os.stat(self._file_full_path)
        except OSError as e:
            if self._print_errors:
                print(f"LogFile[{self.name}]: Log file missing: {e}")
            if hasattr(self, '_file') and self._file:
                try:
                    self._file.close()
                except Exception as e:
                    if self._print_errors:
                        print(f"LogFile[{self.name}]: Failed to close in send(): {e}")
            try:
                self._file = open(self._file_full_path, 'at')
            except Exception as e:
                if self._print_errors:
                    print(f"LogFile[{self.name}]: Failed to reopen file: {e}")

        line = self._prepare_line(level, msg, sys, context, error_id, self._format_timestamp_tuple(timestamp))
        if line is not None:
            print(line, file = self._file)
            self._file.flush()
            size = os.stat(self._file_full_path)[6]
            if size > self._file_size_limit:
                self.log_rotate()

    def log_rotate(self):
        # Pre-compute base path to avoid repeated string operations
        base = self._file_full_path + '.'
        
        # Rotate existing files
        for i in range(self._file_count - 1, 0, -1):
            old_filename = base + str(i)
            new_filename = base + str(i + 1)
            try:
                os.rename(old_filename, new_filename)
            except:
                pass

        # Remove the oldest file
        try:
            os.remove(base + str(self._file_count))
        except:
            pass

        # Close current file and rename it
        try:
            self._file.close()
            os.rename(self._file_full_path, self._file_full_path + '.1')
        except Exception:
            # If rename fails, try to reopen the original file
            try:
                self._file = open(self._file_full_path, 'at')
                return
            except Exception as e:
                if self._print_errors:
                    print(f"LogFile[{self.name}]: Failed to reopen after rotate error: {e}")
        
        # Open new file
        try:
            self._file = open(self._file_full_path, 'at')
        except Exception as e:
            # If we can't open new file, try to recover
            if self._print_errors:
                print(f"LogFile[{self.name}]: Failed to open new file after rotation: {e}")
            self._file = None

    def delete_logs(self):
        try:
            os.remove(self._file_full_path)
        except:
            pass

        for i in range(1, self._file_count):
            try:
                os.remove('{}.{}'.format(self._file_full_path, i))
            except:
                pass
