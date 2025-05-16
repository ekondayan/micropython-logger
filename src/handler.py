from time import localtime
from micropython import const

from .defs import *


class LogHandler:
    _err_title_format = const('{}(#{}): ')
    _timestamp_format = const('{:4d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}')
    _empty_str = const('')  # Pre-interned empty string

    # Use const() for level strings - they're used repeatedly
    _level_map = (
        const('EMERGENCY'),
        const('ALERT'),
        const('CRITICAL'),
        const('ERROR'),
        const('WARNING'),
        const('NOTICE'),
        const('INFORMATION'),
        const('DEBUG')
    )

    def __init__(self, name: str, level: int = L_WARNING):
        if not hasattr(self, '_line_format'):
            raise Exception('LogHandler: Subclass must implement the class variable "_line_format"')

        self.name = name.strip()
        self.level = level

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str) or len(name) == 0:
            raise ValueError('LogHandler: Invalid parameter: name must be non empty string')

        self._name = name.strip().lower()

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level: int):
        if not L_EMERGENCY <= level <= L_DISABLE:
            raise ValueError('LogHandler: Invalid parameter: level can be one of'
                             '[L_EMERGENCY, L_ALERT, L_CRITICAL, L_ERROR, L_WARNING, L_NOTICE, L_INFO, L_DEBUG, L_DISABLE]')

        self._level = level

    def send(self, level, msg, sys=None, context=None, error_id=None, timestamp: tuple = None):
        pass

    def _prepare_line(self, level, msg, sys = None, context = None, error_id = None, timestamp: str = None):
        if self._level == L_DISABLE:
            return None
        elif not isinstance(level, (int, tuple, list)):
            return None
        elif isinstance(level, int) and not L_EMERGENCY <= level <= self._level:
            return None
        elif isinstance(level, (tuple, list)) and not L_EMERGENCY <= level[0] <= self._level:
            return None
        elif msg is not None and not isinstance(msg, str):
            return None
        elif context is not None and not isinstance(context, str):
            return None
        elif not isinstance(timestamp, str):
            return None

        level = self._level_map[level] if isinstance(level, int) else level[1]

        # Optimize dictionary lookup - check existence first
        if sys is not None:
            if sys not in sys_map:
                return None
            sys = sys_map[sys]
        else:
            sys = sys_map[SYS_GENERAL]

        # Optimize error lookup - check existence first
        if error_id is not None:
            if error_id not in errors_map:
                return None
            err_title = self._err_title_format.format(errors_map[error_id], error_id)
        else:
            err_title = self._empty_str

        # Optimize context string operations
        if isinstance(context, str) and context:  # More efficient than len() != 0
            # Combine operations to minimize string manipulations
            if ' ' in context:
                context = '@' + context.replace(' ', '_')
            else:
                context = '@' + context
        else:
            context = self._empty_str

        return self._line_format.format(timestamp = timestamp,
                                        level = level,
                                        sys = sys,
                                        context = context,
                                        err_title = err_title,
                                        msg = msg)
