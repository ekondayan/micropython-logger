micropython-logger

```python
from lib.logger import Logger, defs as logdefs
from lib.logger.file import LogFile
from lib.logger.console import LogConsole
from lib.logger.syslog import LogSyslog

log = Logger()

log.add_handler(LogConsole(level = Logger.level_from_str('DEBUG')))
log.add_handler(LogSyslog('syslog1', level = Logger.level_from_str('WARNING'), host = '127.0.0.1', port = 514, appname = 'YourAppNameHere', log_format = LogSyslog.FORMAT_RFC3164))
log.add_handler(LogSyslog('syslog2', level = Logger.level_from_str('WARNING'), host = '127.0.0.1', port = 514, appname = 'YourAppNameHere', log_format = LogSyslog.FORMAT_RFC5424))
# file_size_limit - set the size limit for the log rotate
# file_count - set the file count limit for the log rotate. For example the following handler will manage 3 log files(system1.log, system1.log.1, system1.log.2)
log.add_handler(LogFile('system1', level = Logger.level_from_str('INFO'), file_path = '/', file_size_limit = 4096, file_count = 3))

log.debug('Test debug')
# 2021-04-30T18:45:34 [DEBUG] GENERAL Test debug

log.info('Test info')
# 2021-04-30T18:45:34 [INFORMATION] GENERAL Test info

log.notice('Test notice')
#2021-04-30T18:45:34 [NOTICE] GENERAL Test notice

log.warn('Test warn')
#2021-04-30T18:45:34 [WARNING] GENERAL Test warn

log.error('Test error')
# 2021-04-30T18:45:35 [ERROR] GENERAL Test error

log.critical('Test critical')
# 2021-04-30T18:45:35 [CRITICAL] GENERAL Test critical

log.alert('Test alert')
# 2021-04-30T18:45:35 [ALERT] GENERAL Test alert

log.emergency('Test emergency')
# 2021-04-30T18:45:35 [EMERGENCY] GENERAL Test emergency

try:
    # sys - the subsystem that this log message is related to
    # context - in what context was it created
    # error_id - an id of the error. The errors can be found in defs.py: errors_map. 
    # exception - raise an exception with the same content as the log message. Must be an Exception subclass
    log.debug('Test2 debug', sys = logdefs.SYS_GENERAL, context = 'function_name', error_id = logdefs.ERROR_UNKNOWN, exception = RuntimeError)
    # 2021-04-30T18:45:35 [DEBUG] GENERAL@function_name Unknown error(#0): Test2 debug
except RuntimeError as e:
    print('Catch an exception {}'.format(e))

# Temporarily disable the handler
log.get_handler('console').level=logdefs.L_DISABLE

# Those two lines do the same thing
log.handlers[3].delete_logs()
file_handler = log.get_handler('system1').delete_logs()
```
# Custom user definitions for 'sys_map' and 'errors_map'
Create a file `logger/user_defs.py`. Inside create two dicts: `sys_map_user`, `errors_map_user`. They will be imported and appended to the ones in the `defs.py`

Here is an example `user_defs.py`:
```python
from micropython import const


SYS_DRIVER = const(1)
SYS_OUTPUT = const(2)
SYS_BUFFER = const(3)
SYS_CONFIG = const(4)
SYS_NTP = const(5)
SYS_WLAN = const(6)

sys_map_user = {
    SYS_DRIVER: 'DRIVER',
    SYS_OUTPUT: 'OUTPUT',
    SYS_BUFFER: 'BUFFER',
    SYS_CONFIG: 'CONFIG',
    SYS_NTP: 'NTP',
    SYS_WLAN: 'WLAN'
}

ERROR_FATAL = const(10)

errors_map_user = {
    ERROR_FATAL: 'Fatal error'
}
```

Bear in mind that `SYS_GENERAL = const(0)` and `ERROR_UNKNOWN = const(0)` are already defined in `defs.py`. That is why `SYS_DRIVER` is assigned the next available number **1**.
