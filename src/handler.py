from time import localtime
from micropython import const

from .defs import LEVEL_NAMES, sys_map, errors_map, SYS_GENERAL, L_EMERGENCY, L_WARNING, L_DISABLE, level_from_str


class LogHandler:
    _err_title_format = const('{}(#{}): ')
    _timestamp_format = const('{:4d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}')
    _empty_str = const('')  # Pre-interned empty string


    def __init__(self, name: str, level: int = L_WARNING, print_errors: bool = False):
        if not hasattr(self, '_line_format'):
            raise ValueError('LogHandler: Subclass must implement the class variable "_line_format"')

        self.name = name  # Let the setter handle stripping and validation
        self.level = level
        self._print_errors = print_errors

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str) or len(name) == 0:
            raise ValueError('LogHandler: Invalid parameter: name must be non empty string')

        stripped_name = name.strip()
        if len(stripped_name) == 0:
            raise ValueError('LogHandler: Invalid parameter: name must be non empty string after stripping whitespace')

        self._name = stripped_name.lower()

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        """Set level from int or string"""
        if isinstance(level, str):
            try:
                level = level_from_str(level)
            except (ValueError, TypeError) as e:
                raise ValueError(f'LogHandler: {e}')
        
        if not isinstance(level, int) or not L_EMERGENCY <= level <= L_DISABLE:
            raise ValueError('LogHandler: Invalid parameter: level must be an integer between L_EMERGENCY(0) and L_DISABLE(8) or a valid level string')

        self._level = level

    def send(self, level, msg, sys = None, context = None, error_id = None, timestamp: tuple = None):
        raise NotImplementedError('Subclass must implement send() method')

    def _format_timestamp_tuple(self, timestamp: tuple):
        """Format timestamp tuple into string. Override for custom formatting."""
        if timestamp is None:
            timestamp = localtime()
        return self._timestamp_format.format(*timestamp[:6])

    def _prepare_line(self, level, msg, sys = None, context = None, error_id = None, timestamp: str = None):
        """Prepare a log line for output.
        
        Args:
            level: Log level - can be:
                   - int: Level constant (L_DEBUG, L_INFO, etc.)
                   - tuple/list: [level_int, level_string] where:
                     [0] = numeric level for filtering
                     [1] = string representation for display
            msg: Log message
            sys: System identifier
            context: Context string
            error_id: Error code identifier  
            timestamp: Formatted timestamp string
            
        Returns:
            Formatted log line or None if filtered
        """
        if self._level == L_DISABLE:
            return None
            
        # Check level type once and branch
        if isinstance(level, int):
            if not L_EMERGENCY <= level <= self._level:
                return None
        elif isinstance(level, (tuple, list)):
            # For tuple/list format: [numeric_level, string_representation]
            if len(level) < 2 or not L_EMERGENCY <= level[0] <= self._level:
                return None
        else:
            return None
            
        # Validate other parameters
        if msg is not None and not isinstance(msg, str):
            return None
        if context is not None and not isinstance(context, str):
            return None
        if timestamp is not None and not isinstance(timestamp, str):
            return None

        # Handle level conversion using LEVEL_NAMES directly
        if isinstance(level, int):
            if 0 <= level < len(LEVEL_NAMES):
                level = LEVEL_NAMES[level]
            else:
                level = 'UNKNOWN'  # For any invalid level beyond our range
        else:
            # For tuple/list, we already validated it has at least 2 elements
            level = level[1]

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
            # Always replace spaces - no-op if none exist
            context = '@' + context.replace(' ', '_')
        else:
            context = self._empty_str

        # Handlers should always provide formatted timestamp
        if timestamp is None:
            # Use current time as fallback
            lt = localtime()
            timestamp = self._timestamp_format.format(*lt[:6])

        return self._line_format.format(timestamp = timestamp,
                                        level = level,
                                        sys = sys,
                                        context = context,
                                        err_title = err_title,
                                        msg = msg)
