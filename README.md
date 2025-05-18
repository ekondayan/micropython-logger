# MicroPython Logger

A lightweight, flexible logging library designed specifically for MicroPython environments. This library provides a logging interface optimized for the memory and performance constraints of embedded systems.

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
- **Runtime Registration**: Dynamic system and error definition with validation
- **Context Support**: Add context information to log messages
- **Error Mapping**: Map error codes to human-readable messages
- **Exception Integration**: Automatically raise exceptions from log messages
- **Debug Support**: Optional error printing for handler debugging

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
git clone https://github.com/ekondayan/micropython-logger.git
cd micropython-logger
```

## Quick Start

```python
from logger import Logger
from logger.console import LogConsole
from logger.file import LogFile
from logger.syslog import LogSyslog
from logger.defs import add_system, add_error, L_DEBUG, L_INFO

# Create a logger instance
log = Logger()

# Define custom systems (names will be automatically converted to uppercase)
SYS_NETWORK = add_system('network')  # Will be stored as 'NETWORK'
SYS_DATABASE = add_system('Database')  # Will be stored as 'DATABASE'

# Define custom errors
ERROR_TIMEOUT = add_error('Connection timeout')
ERROR_INVALID = add_error('Invalid data format')

# Add a console handler that logs DEBUG and above
log.add_handler(LogConsole(level=L_DEBUG))

# Add a file handler that logs INFO and above
log.add_handler(LogFile('app', level=L_INFO, 
                       file_path='/logs', file_size_limit=10240))

# Log some messages
log.debug('Debug message')
log.info('System initialized', sys=SYS_NETWORK)
log.warn('High memory usage', sys=SYS_DATABASE)
log.error('Request failed', sys=SYS_NETWORK, error_id=ERROR_TIMEOUT)
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
from logger.console import LogConsole
from logger.defs import L_WARNING

handler = LogConsole(
    name='console',          # Handler name (optional, default: 'console')
    level=L_WARNING,         # Minimum log level (default: L_WARNING)
    print_errors=False       # Whether to print handler errors (default: False)
)

# Simplest form - all defaults
handler = LogConsole()  # name='console', level=L_WARNING, print_errors=False
```

**Output Format**: `{timestamp} [{level}] {sys}{context} {err_title}{msg}`

### File Handler

Writes log messages to files with automatic rotation.

```python
from logger.file import LogFile

handler = LogFile(
    name='app',             # Base filename (required)
    level=L_WARNING,        # Minimum log level (default: L_WARNING)
    file_path='/',          # Directory path (default: '/')
    file_size_limit=4096,   # Max file size in bytes (default: 4096)
    file_count=3,           # Number of backup files (default: 3)
    print_errors=False      # Whether to print handler errors (default: False)
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
from logger.syslog import LogSyslog

handler = LogSyslog(
    name='syslog',                          # Handler name (required)
    level=L_WARNING,                        # Minimum log level (default: L_WARNING)
    host='192.168.1.100',                   # Syslog server IP
    port=514,                               # Syslog port (default: 514)
    hostname='mydevice',                    # Hostname to report
    appname='myapp',                        # Application name
    log_format=LogSyslog.FORMAT_RFC3164,    # RFC3164 or RFC5424
    timeout=1,                              # Socket timeout in seconds
    print_errors=False                      # Whether to print handler errors (default: False)
)
```

**Supported Formats**:

- `FORMAT_RFC3164`: Traditional BSD syslog format
  - Format: `<{priority}>{timestamp} {hostname} {appname}: {sys}{context} {err_title}{msg}`
  - Priority: log level + 8 (syslog facility)
  - Timestamp: 'Jan 15 10:30:45' format
  
- `FORMAT_RFC5424`: Modern syslog protocol
  - Format: `<{priority}>1 {timestamp} {hostname} {appname} - - - BOM{sys}{context} {err_title}{msg}`
  - Timestamp: ISO 8601 format
  - Includes structured data placeholders

**Features**:

- DNS caching for improved performance
- Non-blocking socket operations
- Automatic facility calculation

## Advanced Usage

### Custom System and Error Definitions

#### Modern API (Recommended)

Use the runtime registration functions to define systems and errors:

```python
from logger.defs import add_system, add_error

# Define custom system identifiers (names are automatically converted to uppercase)
SYS_NETWORK = add_system('Network', 1)   # Stored as 'NETWORK' with ID 1
SYS_SENSOR = add_system('SENSOR', 2)     # Stored as 'SENSOR' with ID 2
SYS_STORAGE = add_system('storage')      # Stored as 'STORAGE' with auto-generated ID

# Define custom error codes
ERROR_TIMEOUT = add_error('Connection timeout', 100)
ERROR_INVALID_DATA = add_error('Invalid data received')  # Auto-generated ID

# Use in logging
log.error('Network timeout', sys=SYS_NETWORK, error_id=ERROR_TIMEOUT)
# Output: 2024-01-15T10:30:45 [ERROR] NETWORK Connection timeout(#100): Network timeout
```

**Features**:
- System names are automatically converted to uppercase for consistency
- Names must be unique (duplicate names raise ValueError)
- IDs can be explicit or auto-generated
- Validation ensures no duplicate IDs or names

#### Legacy API (Backward Compatible)

For existing projects, you can still use the `user_defs.py` approach:

```python
# In logger/user_defs.py
from micropython import const

SYS_NETWORK = const(1)
SYS_SENSOR = const(2)

sys_map_user = {
    SYS_NETWORK: 'NETWORK',
    SYS_SENSOR: 'SENSOR'
}

ERROR_TIMEOUT = const(100)
errors_map_user = {
    ERROR_TIMEOUT: 'Connection timeout'
}
```

**Note**: The legacy approach is maintained for backward compatibility but the modern API is recommended for new projects.

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
    def __init__(self, name: str, level: int = L_WARNING, print_errors: bool = False):
        """Initialize handler with name, level, and error printing option.
        
        Args:
            name: Handler name (will be converted to lowercase)
            level: Minimum log level to process
            print_errors: Whether to print handler errors (e.g., network failures,
                         file access errors) to stdout for debugging
        """

    @property
    def name(self) -> str:
        """Get handler name (always lowercase)."""

    @property
    def level(self) -> int:
        """Get/set handler log level."""

    def send(self, level, msg, sys=None, context=None, error_id=None, timestamp=None):
        """Send a log message (must be implemented by subclasses)."""
```

### Definitions Module Functions

```python
def add_system(name: str, sys_id: int = None) -> int:
    """Register a new system identifier for categorizing log messages.
    
    Args:
        name: System name (will be converted to uppercase)
        sys_id: Optional explicit ID. If None, auto-generates next available ID
        
    Returns:
        int: The system ID to use as a constant
        
    Raises:
        ValueError: If name is empty, already exists, or sys_id is already used
        TypeError: If parameters are wrong type
        
    Example:
        SYS_NETWORK = add_system('network')  # Auto ID, stored as 'NETWORK'
        SYS_DB = add_system('Database', 10)  # ID 10, stored as 'DATABASE'
    """

def add_error(description: str, error_id: int = None) -> int:
    """Register a new error code for structured error reporting.
    
    Args:
        description: Human-readable error description
        error_id: Optional explicit ID. If None, auto-generates next available ID
        
    Returns:
        int: The error ID to use as a constant
        
    Raises:
        ValueError: If description is empty or error_id is already used
        TypeError: If parameters are wrong type
        
    Example:
        ERROR_TIMEOUT = add_error('Connection timeout', 100)
        ERROR_RETRY = add_error('Retry limit exceeded')  # Auto ID
    """
```

## Performance Optimization

This library is optimized for MicroPython environments with several performance enhancements:

1. **Efficient Lookups**: Log level conversions use array/dictionary lookups instead of if/elif chains
2. **Minimal String Operations**: Optimized string building and formatting
3. **DNS Caching**: Syslog handler caches DNS lookups to reduce network overhead
4. **Single Time Calculation**: Timestamp is calculated once and shared among all handlers
5. **Memory-Conscious Design**: Careful use of string interning and object allocation

### Technical Notes

- System names are automatically converted to uppercase for consistency across logs
- The library validates uniqueness of both system IDs and names to prevent confusion
- Handler names are automatically converted to lowercase for consistent lookups

### Memory Usage Tips

- Use higher log levels in production to reduce memory usage
- Limit the number of handlers to what's necessary
- Set appropriate file size limits for file handlers
- Use context and error IDs sparingly

## Examples

### 1. Simplest Usage - Console Only

```python
from logger import Logger
from logger.console import LogConsole

# Create logger with console output
log = Logger()
log.add_handler(LogConsole())

# Basic logging
log.info('Application started')
log.warn('Low memory warning')
log.error('Failed to connect')
```

### 2. Basic Setup with Log Levels

```python
from logger import Logger
from logger.console import LogConsole
from logger.defs import L_DEBUG, L_INFO, L_WARNING, L_ERROR

# Create logger
log = Logger()

# Only show warnings and above in console
log.add_handler(LogConsole(level=L_WARNING))

# These will not be shown (below WARNING level)
log.debug('Debug information')
log.info('Normal operation')

# These will be shown
log.warn('This is important')
log.error('This is critical')
```

### 3. File Logging with Rotation

```python
from logger import Logger
from logger.console import LogConsole
from logger.file import LogFile
from logger.defs import L_DEBUG, L_INFO

# Create logger
log = Logger()

# Console for debugging
log.add_handler(LogConsole(level=L_DEBUG))

# File for permanent record (only INFO and above)
log.add_handler(LogFile(
    name='app',              # Creates app.log
    level=L_INFO,
    file_path='/logs',       # Directory for log files
    file_size_limit=10240,   # Rotate after 10KB
    file_count=3            # Keep 3 backup files
))

log.info('Application started')
log.debug('Debug info - only in console')
```

### 4. Using Systems for Organization

```python
from logger import Logger
from logger.console import LogConsole
from logger.defs import add_system

# Define logical systems (automatically uppercase)
SYS_NETWORK = add_system('network')    # Will be 'NETWORK'
SYS_DATABASE = add_system('database')  # Will be 'DATABASE' 
SYS_AUTH = add_system('auth')          # Will be 'AUTH'

# Create logger
log = Logger()
log.add_handler(LogConsole())

# Log with system context
log.info('Connected to server', sys=SYS_NETWORK)
log.info('User logged in', sys=SYS_AUTH)
log.error('Query failed', sys=SYS_DATABASE)

# Output:
# 2024-01-15T10:30:45 [INFO] NETWORK Connected to server
# 2024-01-15T10:30:46 [INFO] AUTH User logged in
# 2024-01-15T10:30:47 [ERROR] DATABASE Query failed
```

### 5. Error Codes and Structured Errors

```python
from logger import Logger
from logger.console import LogConsole
from logger.defs import add_system, add_error

# Define systems and error codes
SYS_API = add_system('api')
ERROR_TIMEOUT = add_error('Request timeout', 100)
ERROR_AUTH_FAIL = add_error('Authentication failed', 101)
ERROR_INVALID_JSON = add_error('Invalid JSON payload', 102)

# Create logger
log = Logger()
log.add_handler(LogConsole())

# Use error codes for structured logging
log.error('API request failed', 
         sys=SYS_API, 
         error_id=ERROR_TIMEOUT)

# Output:
# 2024-01-15T10:30:45 [ERROR] API Request timeout(#100): API request failed
```

### 6. Context-Aware Logging

```python
from logger import Logger
from logger.console import LogConsole
from logger.defs import add_system, add_error

# Define system and errors
SYS_PROCESSOR = add_system('processor')
ERROR_VALIDATION = add_error('Validation failed')

# Create logger
log = Logger()
log.add_handler(LogConsole())

def process_order(order_id):
    log.info('Processing order', 
            sys=SYS_PROCESSOR, 
            context=f'order_{order_id}')
    
    # Context helps track flow
    log.debug('Validating items', 
             sys=SYS_PROCESSOR, 
             context=f'order_{order_id}.validate')
    
    log.error('Invalid quantity', 
             sys=SYS_PROCESSOR,
             context=f'order_{order_id}.validate',
             error_id=ERROR_VALIDATION)

# Output shows the execution context
# 2024-01-15T10:30:45 [INFO] PROCESSOR@order_123 Processing order
# 2024-01-15T10:30:45 [DEBUG] PROCESSOR@order_123.validate Validating items
# 2024-01-15T10:30:45 [ERROR] PROCESSOR@order_123.validate Validation failed(#1): Invalid quantity
```

### 7. Exception Integration

```python
from logger import Logger
from logger.console import LogConsole
from logger.defs import add_system

SYS_NETWORK = add_system('network')

# Create logger
log = Logger()
log.add_handler(LogConsole())

class NetworkError(Exception):
    pass

# Log and raise exception in one call
try:
    log.error('Connection failed', 
             sys=SYS_NETWORK,
             exception=NetworkError)
except NetworkError as e:
    print(f'Caught: {e}')
    
# Log with existing exception
try:
    raise ValueError('Invalid port')
except ValueError as e:
    log.error('Configuration error', 
             sys=SYS_NETWORK,
             exception=e)  # Re-raises the same exception
```

### 8. Multi-Handler Setup

```python
from logger import Logger
from logger.console import LogConsole
from logger.file import LogFile
from logger.syslog import LogSyslog
from logger.defs import L_DEBUG, L_INFO, L_WARNING, L_ERROR

# Create logger
log = Logger()

# Different handlers for different purposes
log.add_handler(LogConsole(
    name='debug_console',
    level=L_DEBUG
))

log.add_handler(LogFile(
    name='main',
    level=L_INFO,
    file_path='/logs'
))

log.add_handler(LogFile(
    name='errors',
    level=L_ERROR,
    file_path='/logs/errors'
))

log.add_handler(LogSyslog(
    name='remote',
    level=L_WARNING,
    host='192.168.1.100'
))

# Messages go to appropriate handlers based on level
log.debug('Debug info')      # Only console
log.info('Normal message')   # Console + main.log
log.warn('Warning')          # Console + main.log + syslog
log.error('Error')           # All handlers
```

### 9. Dynamic Handler Management

```python
from logger import Logger
from logger.console import LogConsole
from logger.file import LogFile
from logger.defs import L_DEBUG, L_WARNING, L_DISABLE

# Create logger
log = Logger()

# Add handlers
console = LogConsole(name='console', level=L_WARNING)
file_handler = LogFile(name='app', level=L_DEBUG)

log.add_handler(console)
log.add_handler(file_handler)

# Normal operation
log.info('Normal message')

# Temporarily disable console
console.level = L_DISABLE
log.warn('Only in file')  # Won't show in console

# Re-enable with different level
console.level = L_DEBUG
log.debug('Now in both')

# Remove handler completely
log.remove_handler('app')
log.info('Only in console now')

# Get handler by name
handler = log.get_handler('console')
print(f'Console level: {handler.level}')
```

### 10. Custom Timestamp Function

```python
from logger import Logger
from logger.console import LogConsole
import time

# Custom timestamp function (e.g., from RTC)
def rtc_timestamp():
    # Your RTC code here
    # Must return time.struct_time
    return time.localtime()

# Create logger
log = Logger()
log.localtime_callback = rtc_timestamp
log.add_handler(LogConsole())

log.info('Using RTC timestamp')
```

### 11. IoT Device Complete Example

```python
from logger import Logger
from logger.console import LogConsole
from logger.file import LogFile
from logger.syslog import LogSyslog
from logger.defs import L_DEBUG, L_INFO, L_WARNING, L_ERROR
from logger.defs import add_system, add_error

# Define systems
SYS_SENSOR = add_system('sensor')
SYS_NETWORK = add_system('network')
SYS_POWER = add_system('power')

# Define errors
ERROR_SENSOR_TIMEOUT = add_error('Sensor timeout')
ERROR_NETWORK_DOWN = add_error('Network unreachable')
ERROR_LOW_BATTERY = add_error('Battery below threshold')

class IoTDevice:
    def __init__(self):
        self.log = Logger()
        self._setup_logging()
        
    def _setup_logging(self):
        # Console for development
        self.log.add_handler(LogConsole(
            level=L_DEBUG,
            print_errors=True  # Show handler errors
        ))
        
        # Local file for critical issues
        self.log.add_handler(LogFile(
            name='device',
            level=L_WARNING,
            file_path='/flash/logs',
            file_size_limit=8192,  # 8KB limit on flash
            file_count=2           # Only 2 backups
        ))
        
        # Remote syslog when connected
        self.syslog_handler = LogSyslog(
            name='cloud',
            level=L_INFO,
            host='iot.example.com',
            hostname=self.device_id,
            appname='iot-sensor',
            log_format=LogSyslog.FORMAT_RFC5424
        )
        
    def connect_network(self):
        try:
            # Network connection code
            self.log.info('Network connected', sys=SYS_NETWORK)
            # Add syslog handler after network is up
            self.log.add_handler(self.syslog_handler)
        except Exception as e:
            self.log.error('Network connection failed',
                          sys=SYS_NETWORK,
                          error_id=ERROR_NETWORK_DOWN,
                          exception=e)
                          
    def read_sensor(self):
        self.log.debug('Reading sensor', 
                      sys=SYS_SENSOR,
                      context='read_sensor')
        try:
            # Sensor reading code
            value = sensor.read()
            self.log.info(f'Sensor value: {value}',
                         sys=SYS_SENSOR)
            return value
        except TimeoutError:
            self.log.error('Sensor read timeout',
                          sys=SYS_SENSOR,
                          error_id=ERROR_SENSOR_TIMEOUT,
                          context='read_sensor')
            raise
                          
    def check_battery(self):
        level = self.get_battery_level()
        if level < 20:
            self.log.warn('Low battery',
                         sys=SYS_POWER,
                         error_id=ERROR_LOW_BATTERY,
                         context=f'battery_{level}%')
        return level

# Usage
device = IoTDevice()
device.connect_network()
device.read_sensor()
device.check_battery()
```

### 12. Debug vs Production Mode

```python
from logger import Logger
from logger.console import LogConsole
from logger.file import LogFile
from logger.defs import L_DEBUG, L_INFO, L_ERROR

# Simple debug/production setup
def create_logger(debug_mode=False):
    log = Logger()
    
    # Console handler - adjust level based on mode
    log.add_handler(LogConsole(
        level=L_DEBUG if debug_mode else L_ERROR,
        print_errors=debug_mode
    ))
    
    # File handler - always log INFO and above
    log.add_handler(LogFile(
        name='app',
        level=L_INFO,
        file_path='/logs',
        print_errors=debug_mode
    ))
    
    return log

# Usage
debug = __debug__  # Or from config/environment
log = create_logger(debug_mode=debug)

log.debug('Detailed info')  # Only shown in debug mode
log.info('Normal operation')
log.error('Always visible')
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

For more information, bug reports, or feature requests, please visit the [project repository](https://github.com/ekondayan/micropython-logger).
