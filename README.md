micropython-logger



```python
from lib.logger import Logger, defs as logdefs
from lib.logger.file import LogFile
from lib.logger.console import LogConsole
from lib.logger.syslog import LogSyslog

log = Logger()

log.add_handler(LogConsole(level = Logger.level_from_str('DEBUG')))
log.add_handler(LogSyslog('syslog1', level = Logger.level_from_str('WARNING'), ip = '127.0.0.1', port = 514, appname = 'YourAppNameHere', log_format = LogSyslog.FORMAT_RFC3164))
log.add_handler(LogSyslog('syslog2', level = Logger.level_from_str('WARNING'), ip = '127.0.0.1', port = 514, appname = 'YourAppNameHere', log_format = LogSyslog.FORMAT_RFC5424))
log.add_handler(LogFile('system1', level = Logger.level_from_str('INFO'), file_path = '/', file_size_limit = 4096, file_count = 3))

log.debug('Test debug')
log.info('Test info')
log.notice('Test notice')
log.warn('Test warn')
log.error('Test error')
log.critical('Test critical')
log.alert('Test alert')
log.emergency('Test emergency')

log.handlers[3].delete_logs()
file_handler = log.get_handler('system1').delete_logs()
```
