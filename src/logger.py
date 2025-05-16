from time import localtime

from .defs import *


class Logger:
    def __init__(self):
        self._handlers = []
        self._localtime = None

    @staticmethod
    def level_to_str(level: int):
        if level == L_EMERGENCY:
            return 'EMERGENCY'
        elif level == L_ALERT:
            return 'ALERT'
        elif level == L_CRITICAL:
            return 'CRITICAL'
        elif level == L_ERROR:
            return 'ERROR'
        elif level == L_WARNING:
            return 'WARNING'
        elif level == L_NOTICE:
            return 'NOTICE'
        elif level == L_INFO:
            return 'INFO'
        elif level == L_DEBUG:
            return 'DEBUG'
        elif level == L_DISABLE:
            return 'DISABLE'

        raise ValueError('Invalid parameter: parameter "level" must be int that represent a valid severity level')

    @staticmethod
    def level_from_str(level: str):
        level = level.upper()
        if level == 'EMERGENCY':
            return L_EMERGENCY
        elif level == 'ALERT':
            return L_ALERT
        elif level == 'CRITICAL':
            return L_CRITICAL
        elif level == 'ERROR':
            return L_ERROR
        elif level == 'WARNING':
            return L_WARNING
        elif level == 'NOTICE':
            return L_NOTICE
        elif level == 'INFO':
            return L_INFO
        elif level == 'DEBUG':
            return L_DEBUG
        elif level == 'DISABLE':
            return L_DISABLE

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

        _name_low = obj.name.lower()
        for h in self._handlers:
            if h.name.lower() == _name_low:
                raise RuntimeError('Log: A handler with the same name({}) already exists'.format(_name_low))

        self._handlers.append(obj)

    def get_handler(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError('Log: Invalid parameter name={}, expected non empty string'.format(name))

        _name_low = name.lower()
        for h in self._handlers:
            if h.name.lower() == _name_low:
                return h

        return None

    def remove_handler(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError('Log: Invalid parameter name={}, expected non empty string'.format(name))

        _name_low = name.lower()
        for h in self._handlers:
            if h.name.lower() == _name_low:
                self._handlers.remove(h)
                return

        raise RuntimeError('Log: Handler with name={} does not exists'.format(name))

    def log(self, level: int, msg: str, sys, context, error_id, exception = None):
        for h in self._handlers:
            lt = self._localtime() if callable(self._localtime) else localtime()
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


