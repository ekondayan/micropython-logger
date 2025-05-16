from time import localtime

from .defs import LEVEL_NAMES, L_EMERGENCY, L_ALERT, L_CRITICAL, L_ERROR, L_WARNING, L_NOTICE, L_INFO, L_DEBUG, L_DISABLE, level_to_str, level_from_str


class Logger:
    def __init__(self):
        self._handlers = []
        self._localtime = None

    @staticmethod
    def level_to_str(level: int):
        """Convert level int to string - delegated to defs module"""
        try:
            return level_to_str(level)
        except ValueError:
            raise ValueError('Invalid parameter: parameter "level" must be int that represent a valid severity level')

    @staticmethod
    def level_from_str(level: str):
        """Convert level string to int - delegated to defs module"""
        try:
            return level_from_str(level)
        except (ValueError, TypeError):
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
            raise ValueError(f'Log: Invalid parameter obj={obj}, must be a subclass of LogHandler')

        _name_low = obj.name  # Already lowercase from handler
        for h in self._handlers:
            if h.name == _name_low:  # Names are already lowercase
                raise RuntimeError(f'Log: A handler with the same name({_name_low}) already exists')

        self._handlers.append(obj)

    def get_handler(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError(f'Log: Invalid parameter name={name}, expected non empty string')

        _name_low = name.strip().lower()
        for h in self._handlers:
            if h.name == _name_low:  # Handler names are already lowercase
                return h

        return None

    def remove_handler(self, name: str):
        if not isinstance(name, str) or not name:
            raise ValueError(f'Log: Invalid parameter name={name}, expected non empty string')

        _name_low = name.strip().lower()
        for h in self._handlers:
            if h.name == _name_low:  # Handler names are already lowercase
                self._handlers.remove(h)
                return

        raise RuntimeError(f'Log: Handler with name={name} does not exists')

    def log(self, level: int, msg: str, sys, context, error_id, exception = None):
        # Cache list reference - faster than multiple attribute lookups
        handlers = self._handlers
        
        # Early exit if nothing to do  
        if not handlers and exception is None:
            return
            
        # Calculate localtime once for all handlers
        if handlers:
            lt = self._localtime() if callable(self._localtime) else localtime()
            for h in handlers:
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
