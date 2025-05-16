# MicroPython Logger

A lightweight, flexible logging library designed specifically for MicroPython environments. This library provides a familiar logging interface similar to Python's standard logging module while being optimized for the memory and performance constraints of embedded systems.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Log Levels](#log-levels)
- [Handlers](#handlers)
  - [Console Handler](#console-handler)
  - [File Handler](#file-handler)
  - [Syslog Handler](#syslog-handler)
- [Advanced Usage](#advanced-usage)
  - [Custom System and Error Definitions](#custom-system-and-error-definitions)
  - [Exception Integration](#exception-integration)
  - [Handler Management](#handler-management)
  - [Custom Timestamp Function](#custom-timestamp-function)
- [API Reference](#api-reference)
- [Performance Optimization](#performance-optimization)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multiple Log Levels**: Support for standard syslog severity levels (Emergency through Debug)
- **Multiple Handlers**: Console, file, and syslog handlers with different configuration options
- **File Rotation**: Automatic log file rotation based on file size
- **Syslog Support**: Both RFC3164 and RFC5424 syslog formats
- **Memory Efficient**: Optimized for MicroPython's constrained environments
- **Extensible**: Easy to add custom handlers and extend functionality
- **Context Support**: Add context information to log messages
- **Error Mapping**: Map error codes to human-readable messages
- **Exception Integration**: Automatically raise exceptions from log messages

## Installation

### For MicroPython

1. Copy the `src` directory to your MicroPython device's `/lib/logger/` directory
2. Ensure the directory structure is maintained:
   
   ```
   /lib/logger/
   ├── __init__.py
   ├── logger.py
   ├── handler.py
   ├── console.py
   ├── file.py
   ├── syslog.py
   └── defs.py
   ```

### For Development/Testing

```bash
git clone https://github.com/your-repo/micropython-logger.git
cd micropython-logger
```

## Quick Start

```python
from lib.logger import Logger
from lib.logger.console import LogConsole
from lib.logger.file import LogFile
from lib.logger.syslog import LogSyslog

# Create a logger instance
log = Logger()

# Add a console handler that logs DEBUG and above
log.add_handler(LogConsole(level=Logger.level_from_str('DEBUG')))

# Add a file handler that logs INFO and above
log.add_handler(LogFile('app', level=Logger.level_from_str('INFO'), 
                       file_path='/logs', file_size_limit=10240))

# Log some messages
log.debug('Debug message')
log.info('Information message')
log.warn('Warning message')
log.error('Error message')
```

## Architecture

The library follows a modular architecture:

- **Logger**: Central logging interface that manages handlers
- **Handler**: Base class for all log destinations
- **Formatters**: Built into handlers, format messages according to handler-specific patterns
- **Definitions**: Constants and mappings for log levels and error codes

## Log Levels

The library supports standard syslog severity levels:

| Level     | Constant      | Value | Description                       |
| --------- | ------------- | ----- | --------------------------------- |
| Emergency | `L_EMERGENCY` | 0     | System is unusable                |
| Alert     | `L_ALERT`     | 1     | Action must be taken immediately  |
| Critical  | `L_CRITICAL`  | 2     | Critical conditions               |
| Error     | `L_ERROR`     | 3     | Error conditions                  |
| Warning   | `L_WARNING`   | 4     | Warning conditions                |
| Notice    | `L_NOTICE`    | 5     | Normal but significant conditions |
| Info      | `L_INFO`      | 6     | Informational messages            |
| Debug     | `L_DEBUG`     | 7     | Debug-level messages              |
| Disable   | `L_DISABLE`   | 8     | Disable the handler               |

## Handlers

### Console Handler

Outputs log messages to the console (stdout).

```python
from lib.logger.console import LogConsole

handler = LogConsole(
    name='console',          # Handler name (optional, default: 'console')
    level=L_WARNING         # Minimum log level (default: L_WARNING)
)
```

**Output Format**: `{timestamp} [{level}] {sys}{context} {err_title}{msg}`

### File Handler

Writes log messages to files with automatic rotation.

```python
from lib.logger.file import LogFile

handler = LogFile(
    name='app',             # Base filename (required)
    level=L_WARNING,        # Minimum log level (default: L_WARNING)
    file_path='/',          # Directory path (default: '/')
    file_size_limit=4096,   # Max file size in bytes (default: 4096)
    file_count=3           # Number of backup files (default: 3)
)
```

**Features**:

- Automatic file rotation when size limit is reached
- Maintains specified number of backup files (e.g., app.log, app.log.1, app.log.2)
- Creates new files automatically if deleted

**Output Format**: `{timestamp} [{level}] {sys}{context} {err_title}{msg}`

### Syslog Handler

Sends log messages to a syslog server via UDP.

```python
from lib.logger.syslog import LogSyslog

handler = LogSyslog(
    name='syslog',                          # Handler name (required)
    level=L_WARNING,                        # Minimum log level (default: L_WARNING)
    host='192.168.1.100',                   # Syslog server IP
    port=514,                               # Syslog port (default: 514)
    hostname='mydevice',                    # Hostname to report
    appname='myapp',                        # Application name
    log_format=LogSyslog.FORMAT_RFC3164,    # RFC3164 or RFC5424
    timeout=1                               # Socket timeout in seconds
)
```

**Supported Formats**:

- `FORMAT_RFC3164`: Traditional BSD syslog format
- `FORMAT_RFC5424`: Modern syslog protocol

**Features**:

- DNS caching for improved performance
- Non-blocking socket operations
- Automatic facility calculation

## Advanced Usage

### Custom System and Error Definitions

Create a `user_defs.py` file in the logger directory:

```python
from micropython import const

# Define custom system identifiers
SYS_NETWORK = const(1)
SYS_SENSOR = const(2)
SYS_STORAGE = const(3)

sys_map_user = {
    SYS_NETWORK: 'NETWORK',
    SYS_SENSOR: 'SENSOR',
    SYS_STORAGE: 'STORAGE'
}

# Define custom error codes
ERROR_TIMEOUT = const(1)
ERROR_INVALID_DATA = const(2)

errors_map_user = {
    ERROR_TIMEOUT: 'Operation timed out',
    ERROR_INVALID_DATA: 'Invalid data received'
}
```

Usage:

```python
from lib.logger import defs

log.error('Network timeout', sys=defs.SYS_NETWORK, error_id=defs.ERROR_TIMEOUT)
# Output: 2024-01-15T10:30:45 [ERROR] NETWORK Operation timed out(#1): Network timeout
```

### Exception Integration

Automatically raise exceptions from log messages:

```python
try:
    log.error('Critical failure', exception=RuntimeError)
except RuntimeError as e:
    print(f'Caught: {e}')

# Or with custom exception classes
class CustomError(Exception):
    pass

log.critical('System failure', exception=CustomError)
```

### Handler Management

```python
# Get handler by name
console_handler = log.get_handler('console')

# Temporarily disable a handler
console_handler.level = L_DISABLE

# Re-enable with a different level
console_handler.level = L_INFO

# Remove a handler
log.remove_handler('console')

# Access all handlers
for handler in log.handlers:
    print(f'Handler: {handler.name}, Level: {handler.level}')
```

### Custom Timestamp Function

Provide a custom timestamp function for specialized time sources:

```python
import time

def custom_timestamp():
    # Return time from RTC, NTP, or other source
    return time.localtime()

log.localtime_callback = custom_timestamp
```

## API Reference

### Logger Class

```python
class Logger:
    def __init__(self):
        """Initialize a new logger instance."""

    def add_handler(self, handler: LogHandler):
        """Add a handler to the logger."""

    def remove_handler(self, name: str):
        """Remove a handler by name."""

    def get_handler(self, name: str) -> LogHandler:
        """Get a handler by name."""

    def debug(self, msg: str, sys=None, context=None, error_id=None, exception=None):
        """Log a debug message."""

    def info(self, msg: str, sys=None, context=None, error_id=None, exception=None):
        """Log an informational message."""

    def notice(self, msg: str, sys=None, context=None, error_id=None, exception=None):
        """Log a notice message."""

    def warn(self, msg: str, sys=None, context=None, error_id=None, exception=None):
        """Log a warning message."""

    def error(self, msg: str, sys=None, context=None, error_id=None, exception=None):
        """Log an error message."""

    def critical(self, msg: str, sys=None, context=None, error_id=None, exception=None):
        """Log a critical message."""

    def alert(self, msg: str, sys=None, context=None, error_id=None, exception=None):
        """Log an alert message."""

    def emergency(self, msg: str, sys=None, context=None, error_id=None, exception=None):
        """Log an emergency message."""

    @staticmethod
    def level_to_str(level: int) -> str:
        """Convert log level to string."""

    @staticmethod
    def level_from_str(level: str) -> int:
        """Convert string to log level."""
```

### LogHandler Base Class

```python
class LogHandler:
    def __init__(self, name: str, level: int = L_WARNING):
        """Initialize handler with name and level."""

    @property
    def name(self) -> str:
        """Get handler name (always lowercase)."""

    @property
    def level(self) -> int:
        """Get/set handler log level."""

    def send(self, level, msg, sys=None, context=None, error_id=None, timestamp=None):
        """Send a log message (must be implemented by subclasses)."""
```

## Performance Optimization

This library is optimized for MicroPython environments with several performance enhancements:

1. **String Interning**: Frequently used strings are interned using `const()` to reduce memory allocation
2. **Efficient Lookups**: Log level conversions use array/dictionary lookups instead of if/elif chains
3. **Minimal String Operations**: Optimized string building and formatting
4. **DNS Caching**: Syslog handler caches DNS lookups to reduce network overhead
5. **Single Time Calculation**: Timestamp is calculated once and shared among all handlers

### Memory Usage Tips

- Use higher log levels in production to reduce memory usage
- Limit the number of handlers to what's necessary
- Set appropriate file size limits for file handlers
- Use context and error IDs sparingly

## Examples

### Basic Logging Setup

```python
from lib.logger import Logger, defs as logdefs
from lib.logger.console import LogConsole
from lib.logger.file import LogFile

# Create logger
log = Logger()

# Console for debugging
log.add_handler(LogConsole(level=logdefs.L_DEBUG))

# File for important messages
log.add_handler(LogFile('system', 
                       level=logdefs.L_INFO,
                       file_path='/logs',
                       file_size_limit=10240,
                       file_count=5))

# Use the logger
log.info('System started')
log.debug('Debug mode enabled')
```

### IoT Device Example

```python
from lib.logger import Logger, defs
from lib.logger.syslog import LogSyslog
from lib.logger.file import LogFile

# Setup for an IoT device
log = Logger()

# Local file logging for critical errors
log.add_handler(LogFile('device',
                       level=defs.L_ERROR,
                       file_path='/flash/logs',
                       file_size_limit=4096))

# Remote syslog for monitoring
log.add_handler(LogSyslog('remote',
                         level=defs.L_WARNING,
                         host='log.example.com',
                         port=514,
                         hostname='sensor-001',
                         appname='temperature-monitor'))

# Log sensor data
def read_sensor():
    try:
        temperature = sensor.read_temperature()
        if temperature > 50:
            log.warn('High temperature detected', 
                    sys=defs.SYS_SENSOR,
                    context='read_sensor',
                    error_id=defs.ERROR_HIGH_TEMP)
        return temperature
    except Exception as e:
        log.error('Sensor read failed',
                 sys=defs.SYS_SENSOR,
                 context='read_sensor',
                 exception=e)
        raise
```

### Context-Aware Logging

```python
class DataProcessor:
    def __init__(self, logger):
        self.log = logger

    def process_data(self, data):
        self.log.debug('Processing started',
                      context='process_data')

        if not self.validate_data(data):
            self.log.error('Invalid data format',
                          context='process_data.validate',
                          error_id=ERROR_INVALID_FORMAT)
            return False

        try:
            result = self.transform_data(data)
            self.log.info('Processing completed',
                         context='process_data')
            return result
        except Exception as e:
            self.log.critical('Processing failed',
                             context='process_data.transform',
                             exception=e)
            raise
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies
4. Run tests

### Code Style

- Follow PEP 8 guidelines where applicable to MicroPython
- Use meaningful variable and function names
- Add docstrings to all public methods
- Keep MicroPython constraints in mind

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Optimized for MicroPython's unique constraints

---

For more information, bug reports, or feature requests, please visit the [project repository]([GitHub - ekondayan/micropython-logger: Simple but powerfull micropython logging library](https://github.com/ekondayan/micropython-logger).