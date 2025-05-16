from time import localtime

from .defs import *


class Logger:
    def __init__(self):
        self._handlers = []
        self._localtime = None

    # Pre-computed level string mapping for O(1) lookup
    _LEVEL_TO_STR = (
        'EMERGENCY',  # 0
        'ALERT',      # 1
        'CRITICAL',   # 2
        'ERROR',      # 3
        'WARNING',    # 4
        'NOTICE',     # 5
        'INFO',       # 6
        'DEBUG',      # 7
        'DISABLE'     # 8
    )
    
    @staticmethod
    def level_to_str(level: int):
        if 0 <= level <= 8:
            return Logger._LEVEL_TO_STR[level]
        raise ValueError('Invalid parameter: parameter "level" must be int that represent a valid severity level')

    # Pre-computed string to level mapping for O(1) lookup
    _STR_TO_LEVEL = {
        'EMERGENCY': L_EMERGENCY,
        'ALERT': L_ALERT,
        'CRITICAL': L_CRITICAL,
        'ERROR': L_ERROR,
        'WARNING': L_WARNING,
        'NOTICE': L_NOTICE,
        'INFO': L_INFO,
        'DEBUG': L_DEBUG,
        'DISABLE': L_DISABLE
    }
    
    @staticmethod
    def level_from_str(level: str):
        level_upper = level.upper()
        if level_upper in Logger._STR_TO_LEVEL:
            return Logger._STR_TO_LEVEL[level_upper]
        raise ValueError('Invalid parameter: parameter "level" must be str that represent a valid severity level')

    @property
    def localtime_callback(self):
        return self._localtime

    @localtime_callback.setter
    def localtime_callback(self, callback):
        if callable(callback) or callback is None:
            self._localtime = callback

    @property
    def handlers(self):
        return self._handlers

    def add_handler(self, obj):
        from .handler import LogHandler

        if not isinstance(obj, LogHandler):
            raise ValueError('Log: Invalid parameter obj={}, must be a subclass of LogHandler'.format(obj))

        _name_low = obj.name  # Already lowercase from handler
        for h in self._handlers:
            if h.name == _name_low:  # Names are already lowercase
                raise RuntimeError('Log: A handler with the same name({}) already exists'.format(_name_low))

        self._handlers.append(obj)

    def get_handler(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError('Log: Invalid parameter name={}, expected non empty string'.format(name))

        _name_low = name.strip().lower()
        for h in self._handlers:
            if h.name == _name_low:  # Handler names are already lowercase
                return h

        return None

    def remove_handler(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError('Log: Invalid parameter name={}, expected non empty string'.format(name))

        _name_low = name.strip().lower()
        for h in self._handlers:
            if h.name == _name_low:  # Handler names are already lowercase
                self._handlers.remove(h)
                return

        raise RuntimeError('Log: Handler with name={} does not exists'.format(name))

    def log(self, level: int, msg: str, sys, context, error_id, exception = None):
        # Calculate localtime once for all handlers
        if self._handlers:  # Only calculate if we have handlers
            lt = self._localtime() if callable(self._localtime) else localtime()
            for h in self._handlers:
                h.send(level, msg, sys, context, error_id, lt)

        if exception is not None:
            if isinstance(exception, type) and issubclass(exception, Exception):
                raise exception(msg)
            elif isinstance(exception, Exception):
                raise exception

    def emergency(self, msg: str, sys = None, context = None, error_id = None, exception = None):
        self.log(L_EMERGENCY, msg, sys, context, error_id, exception)

    def alert(self, msg: str, sys = None, context = None, error_id = None, exception = None):
        self.log(L_ALERT, msg, sys, context, error_id, exception)

    def critical(self, msg: str, sys = None, context = None, error_id = None, exception = None):
        self.log(L_CRITICAL, msg, sys, context, error_id, exception)

    def error(self, msg: str, sys = None, context = None, error_id = None, exception = None):
        self.log(L_ERROR, msg, sys, context, error_id, exception)

    def warn(self, msg: str, sys = None, context = None, error_id = None, exception = None):
        self.log(L_WARNING, msg, sys, context, error_id, exception)

    def notice(self, msg: str, sys = None, context = None, error_id = None, exception = None):
        self.log(L_NOTICE, msg, sys, context, error_id, exception)

    def info(self, msg: str, sys = None, context = None, error_id = None, exception = None):
        self.log(L_INFO, msg, sys, context, error_id, exception)

    def debug(self, msg: str, sys = None, context = None, error_id = None, exception = None):
        self.log(L_DEBUG, msg, sys, context, error_id, exception)


