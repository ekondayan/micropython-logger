from .defs import *

class Logger:
    def __init__(self):
        self._handlers = []

    @property
    def handlers(self):
        return self._handlers

    def add_handler(self, obj):
        from .handler import LogHandler

        if not isinstance(obj, LogHandler):
            raise ValueError('Log: Invalid parameter obj={}, must be a subclass of LogHandler'.format(name))

        _name_low = obj.name
        for h in self._handlers:
            if h.name == _name_low:
                raise RuntimeError('Log: A handler with the same name({}) already exists'.format(_name_low))

        self._handlers.append(obj)

    def get_handler(self, name):
        if not isinstance(name, str) or not name:
            raise ValueError('Log: Invalid parameter name={}, expected non empty string'.format(name))

        _name_low = name.strip().lower()
        for h in self._handlers:
            if h.name == _name_low:
                return h

        return None

    def remove_handler(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError('Log: Invalid parameter name={}, expected non empty string'.format(name))

        _name_low = name.strip().lower()
        for h in self._handlers:
            if h.name == _name_low:
                self._handlers.remove(h)
                return

        raise RuntimeError('Log: Handler with name={} does not exists'.format(name))

    def log(self, level, msg, sys, context, error_id, exception = None):
        for h in self._handlers:
            h.send(level, msg, sys, context, error_id)

        if type(exception).__name__ == 'type' and issubclass(exception, Exception):
            raise exception(msg)

    def emergency(self, msg, sys = None, context = None, error_id = None, exception = None):
        self.log(L_EMERGENCY, msg, sys, context, error_id, exception)

    def alert(self, msg, sys = None, context = None, error_id = None, exception = None):
        self.log(L_ALERT, msg, sys, context, error_id, exception)

    def critical(self, msg, sys = None, context = None, error_id = None, exception = None):
        self.log(L_CRITICAL, msg, sys, context, error_id, exception)

    def error(self, msg, sys = None, context = None, error_id = None, exception = None):
        self.log(L_ERROR, msg, sys, context, error_id, exception)

    def warn(self, msg, sys = None, context = None, error_id = None, exception = None):
        self.log(L_WARNING, msg, sys, context, error_id, exception)

    def notice(self, msg, sys = None, context = None, error_id = None, exception = None):
        self.log(L_NOTICE, msg, sys, context, error_id, exception)

    def info(self, msg, sys = None, context = None, error_id = None, exception = None):
        self.log(L_INFO, msg, sys, context, error_id, exception)

    def debug(self, msg, sys = None, context = None, error_id = None, exception = None):
        self.log(L_DEBUG, msg, sys, context, error_id, exception)


