from micropython import const


L_EMERGENCY = const(0)
L_ALERT= const(1)
L_CRITICAL = const(2)
L_ERROR = const(3)
L_WARNING = const(4)
L_NOTICE = const(5)
L_INFO = const(6)
L_DEBUG = const(7)
L_DISABLE = const(8)

SYS_GENERAL = const(0)

ERROR_UNKNOWN = const(0)

sys_map = {
    SYS_GENERAL: 'GENERAL',
}

errors_map = {
    ERROR_UNKNOWN: 'Unknown error',
}

try:
    from logger.user_defs import *
except ImportError:
    pass
else:
    sys_map.update(sys_map_user)
    errors_map.update(errors_map_user)

    del sys_map_user
    del errors_map_user