import usocket
from time import localtime
from micropython import const

from .defs import *
from .handler import LogHandler


class LogSyslog(LogHandler):
    FORMAT_RFC3164 = const(0)
    FORMAT_RFC5424 = const(1)

    __months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    _rfc3164_timestamp_format = '{} {:2d} {:02d}:{:02d}:{:02d}'
    _rfc3164_format = '<{level}>{timestamp}%s%s {sys}{context} {err_title}{msg}'
    _rfc5424_format = '<{level}>1 {timestamp} %s %s - - - BOM{sys}{context} {err_title}{msg}'

    def __init__(self, name, level = L_WARNING, host = None, port: int = 514, hostname: str = None, appname = None, log_format: int = FORMAT_RFC3164, timeout: int = 1):
        if not isinstance(log_format, int) or not self.FORMAT_RFC3164 <= log_format <= self.FORMAT_RFC5424:
            raise ValueError('Invalid parameter: log_format={} must be one of [FORMAT_RFC3164, FORMAT_RFC5424]'.format(log_format))

        self._log_format = log_format
        self._host = host
        self._port = port
        self._timeout = timeout
        self._addr = None


        if log_format == self.FORMAT_RFC3164:
            hostname = ' %s' % hostname if isinstance(hostname, str) else ' '
            appname = ' %s:' % appname if isinstance(appname, str) else ''
            self._line_format = self._rfc3164_format % (hostname, appname)
        else:
            hostname = hostname if isinstance(hostname, str) else '-'
            appname = appname if isinstance(appname, str) else '-'
            self._line_format = self._rfc5424_format % (hostname, appname)

        super().__init__(name, level)

    def send(self, level, msg, sys = None, context = None, error_id = None):
        if self._log_format == self.FORMAT_RFC3164:
            lt = localtime()
            timestamp = self._rfc3164_timestamp_format.format(self.__months[lt[1] - 1], lt[2], lt[3], lt[4], lt[5])
        else:
            timestamp = None

        line = self._prepare_line((level, str(level + (1 << 3))), msg, sys, context, error_id, timestamp = timestamp)
        if line is not None:
            if self._addr is None:
                self._addr = usocket.getaddrinfo(self._host, self._port, 0, usocket.SOCK_DGRAM)[0][-1]

            s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
            s.settimeout(self._timeout)
            s.sendto(line.encode('utf-8'), self._addr)

