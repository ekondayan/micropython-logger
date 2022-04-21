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

    def __init__(self, name: str, level: int = L_WARNING, host = None, port: int = 514, hostname: str = None, appname: str = None, log_format: int = FORMAT_RFC3164, timeout: int = 1):
        if log_format not in (self.FORMAT_RFC3164, self.FORMAT_RFC5424):
            raise ValueError('Invalid parameter: log_format={} must be one of FORMAT_RFC3164, FORMAT_RFC5424]'.format(log_format))

        self._log_format = log_format
        self._host = host
        self._port = port
        self._timeout = timeout
        self._sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        self._sock.settimeout(self._timeout)

        if log_format == self.FORMAT_RFC3164:
            hostname = ' %s' % hostname if isinstance(hostname, str) else ' '
            appname = ' %s:' % appname if isinstance(appname, str) else ''
            self._line_format = self._rfc3164_format % (hostname, appname)
        else:
            hostname = hostname if isinstance(hostname, str) else '-'
            appname = appname if isinstance(appname, str) else '-'
            self._line_format = self._rfc5424_format % (hostname, appname)

        super().__init__(name, level)

    def __del__(self):
        self._sock.close()

    def send(self, level: int, msg: str, sys = None, context = None, error_id = None, timestamp: tuple = None):
        if self._log_format == self.FORMAT_RFC3164:
            timestamp = self._rfc3164_timestamp_format.format(self.__months[timestamp[1] - 1], timestamp[2], timestamp[3], timestamp[4], timestamp[5])
        else:
            timestamp = self._timestamp_format.format(timestamp[0], timestamp[1], timestamp[2],
                                                      timestamp[3], timestamp[4], timestamp[5])

        line = self._prepare_line((level, str(level + 8)), msg, sys, context, error_id, timestamp = timestamp)
        if line is not None:
            try:
                addr = usocket.getaddrinfo(self._host, self._port, 0, usocket.SOCK_DGRAM)[0][-1]
                self._sock.sendto(line.encode('utf-8'), addr)
            except OSError:
                pass
