from time import localtime

from .defs import *


class LogHandler:
    _err_title_format = '{}(#{}): '
    _timestamp_format = '{:4d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}'

    _level_map = (
        'EMERGENCY',
        'ALERT',
        'CRITICAL',
        'ERROR',
        'WARNING',
        'NOTICE',
        'INFORMATION',
        'DEBUG'
    )

    def __init__(self, name, level = L_WARNING):
        if not hasattr(self, '_line_format'):
            raise Exception('LogHandler: Subclass must implement the class variable "_line_format"')

        self.name = name
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
            raise ValueError('LogHandler: Invalid parameter: _level can be one of'
                             '[L_EMERGENCY, L_ALERT, L_CRITICAL, L_ERROR, L_WARNING, L_NOTICE, L_INFO, L_DEBUG, L_DISABLE]')

        self._level = level

    def send(self, level, msg, sys = None, context = None, error_id = None):
        pass

    def _prepare_line(self, level, msg, sys = None, context = None, error_id = None, timestamp = None):
        if self._level == L_DISABLE:
            return None
        elif not isinstance(level, (int, str)):
            return None
        elif isinstance(level, int) and not L_EMERGENCY <= level <= self._level:
            return None
        elif msg is not None and not isinstance(msg, str):
            return None
        elif context is not None and not isinstance(context, str):
            return None
        elif timestamp is not None and not isinstance(timestamp, str):
            return None

        level = self._level_map[level] if isinstance(level, int) else level

        try:
            sys = sys_map[sys] if sys is not None else sys_map[SYS_GENERAL]
        except IndexError:
            return None

        try:
            err_title = self._err_title_format.format(errors_map[error_id], error_id) if error_id is not None else ''
        except IndexError:
            return None

        if isinstance(context, str):
            if len(context) != 0:
                context = '@%s' % context

            if ' ' in context:
                context = context.replace(' ', '_')
        else:
            context = ''

        if timestamp is None:
            lt = localtime()
            timestamp = self._timestamp_format.format(lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])

        return self._line_format.format(timestamp = timestamp,
                                        level = level,
                                        sys = sys,
                                        context = context,
                                        err_title = err_title,
                                        msg = msg)
