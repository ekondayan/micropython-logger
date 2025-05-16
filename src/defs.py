"""
MicroPython Logger Definitions Module

This module provides the foundation for the logging system's categorization and filtering
capabilities. It defines severity levels, system identifiers, and error codes that enable
structured logging across your MicroPython application.

Key Components:
- Logging Levels: Priority-based message filtering (L_EMERGENCY to L_DEBUG)
- System Identifiers: Categorize log messages by subsystem/component
- Error Codes: Map numeric codes to human-readable error descriptions
- Registration Functions: Runtime extension of systems and errors

Usage Patterns:

1. Modern API (Recommended):
   ```python
   from logger.defs import add_system, add_error, L_WARNING
   
   # Register systems with explicit IDs
   SYS_NETWORK = add_system('NETWORK', 1)
   SYS_SENSOR = add_system('SENSOR', 2)
   
   # Or use auto-generated IDs
   SYS_STORAGE = add_system('STORAGE')
   
   # Register error codes
   ERROR_TIMEOUT = add_error('Connection timeout', 10)
   ERROR_SENSOR_FAIL = add_error('Sensor reading failed')
   ```

2. Legacy API (user_defs.py):
   ```python
   # In logger/user_defs.py
   from micropython import const
   
   SYS_NETWORK = const(1)
   sys_map_user = {SYS_NETWORK: 'NETWORK'}
   
   ERROR_TIMEOUT = const(10)
   errors_map_user = {ERROR_TIMEOUT: 'Connection timeout'}
   ```

Best Practices:
- Use consistent ID ranges (e.g., systems: 1-99, errors: 100-999)
- Define constants for IDs to avoid magic numbers in code
- Keep error descriptions concise but informative
- Document your system IDs and error codes for team reference

Note: The modern API supports auto-generated IDs when None is passed, making it
easier to extend the system without managing ID conflicts.
"""

from micropython import const

# === LOGGING LEVELS ===
# Priority-based severity levels for filtering log messages.
# Lower numeric values indicate higher severity.
# Only messages with level <= handler.level will be processed.

L_EMERGENCY = const(0)  # System is unusable (e.g., device failure, critical hardware error)
L_ALERT = const(1)      # Immediate action required (e.g., temperature critical, memory exhausted)
L_CRITICAL = const(2)   # Critical error conditions (e.g., application crash, data corruption)
L_ERROR = const(3)      # Error conditions (e.g., operation failed, invalid input)
L_WARNING = const(4)    # Warning conditions (e.g., low memory, deprecated feature) [DEFAULT]
L_NOTICE = const(5)     # Normal but significant (e.g., configuration change, user login)
L_INFO = const(6)       # Informational messages (e.g., server started, file processed)
L_DEBUG = const(7)      # Detailed debug information (e.g., variable values, function entry/exit)
L_DISABLE = const(8)    # Special level to completely disable a handler

# === LEVEL NAME MAPPING ===
# String representations of logging levels indexed by their numeric value.
# Used internally for log formatting and level string conversion.
LEVEL_NAMES = (
    'EMERGENCY',  # 0 - L_EMERGENCY: System unusable
    'ALERT',      # 1 - L_ALERT: Immediate action required
    'CRITICAL',   # 2 - L_CRITICAL: Critical conditions
    'ERROR',      # 3 - L_ERROR: Error conditions
    'WARNING',    # 4 - L_WARNING: Warning conditions
    'NOTICE',     # 5 - L_NOTICE: Normal but significant
    'INFO',       # 6 - L_INFO: Informational messages  
    'DEBUG',      # 7 - L_DEBUG: Debug messages
    'DISABLE',    # 8 - L_DISABLE: Handler disabled
)

# === LEVEL CONVERSION UTILITIES ===
# These functions handle conversion between numeric levels and their string representations.
# They exist here to avoid circular imports between logger.py and handler.py.

def level_to_str(level):
    """Convert numeric log level to its string representation.
    
    Args:
        level: Integer log level (0-8)
        
    Returns:
        String representation (e.g., 'DEBUG', 'INFO', 'ERROR')
        
    Raises:
        ValueError: If level is outside valid range (0-8)
        
    Example:
        >>> level_to_str(L_DEBUG)
        'DEBUG'
        >>> level_to_str(3)
        'ERROR'
    """
    if 0 <= level <= 8:
        return LEVEL_NAMES[level]
    raise ValueError('Invalid level: must be int between 0-8')

def level_from_str(level_str):
    """Convert log level string to its numeric value.
    
    Args:
        level_str: Case-insensitive level name (e.g., 'debug', 'INFO', 'Error')
        
    Returns:
        Integer level constant (0-8)
        
    Raises:
        TypeError: If level_str is not a string
        ValueError: If level_str is not a recognized level name
        
    Special:
        Accepts 'INFORMATION' as an alias for 'INFO' (backward compatibility)
        
    Example:
        >>> level_from_str('DEBUG')
        7
        >>> level_from_str('error')
        3
        >>> level_from_str('INFORMATION')  # Legacy alias
        6
    """
    if not isinstance(level_str, str):
        raise TypeError('Level must be a string')
    level_upper = level_str.upper()
    if level_upper in LEVEL_NAMES:
        return LEVEL_NAMES.index(level_upper)
    # Check aliases for backward compatibility
    if level_upper == 'INFORMATION':
        return L_INFO
    raise ValueError(f'Invalid level string: {level_str}')

# === SYSTEM IDENTIFIERS ===
# System identifiers categorize log messages by component or subsystem.
# This enables filtering and analysis of logs from specific parts of your application.

SYS_GENERAL = const(0)  # Default system identifier for uncategorized messages

# System identifier mapping: ID -> Name
# Maps numeric system IDs to human-readable names for log formatting.
# Extended at runtime via add_system() or user_defs.py
sys_map = {
    SYS_GENERAL: const('GENERAL'),  # Default system
}

# === ERROR CODES ===
# Error codes provide structured error reporting with numeric identifiers.
# This enables programmatic error handling and standardized error messages.

ERROR_UNKNOWN = const(0)  # Default error code for unspecified errors

# Error code mapping: ID -> Description
# Maps numeric error codes to descriptive messages.
# Extended at runtime via add_error() or user_defs.py
errors_map = {
    ERROR_UNKNOWN: const('Unknown error'),  # Default error
}

# === RUNTIME EXTENSION API ===
# These functions allow dynamic registration of system identifiers and error codes
# at runtime, providing flexibility for modular applications.

def add_system(name, sys_id=None):
    """Register a new system identifier for categorizing log messages.
    
    System identifiers help organize logs by component, making it easier to:
    - Filter logs from specific subsystems
    - Analyze component-specific issues
    - Route logs to appropriate handlers
    
    Args:
        name: Human-readable system name (str, required)
              Will be displayed in log messages
        sys_id: Unique identifier for the system (int or None, optional)
                If None, automatically generates the next available ID
              
    Returns:
        int: The system ID (const-wrapped if available) for use as a constant
        
    Raises:
        ValueError: If name is empty/whitespace or sys_id already exists
        TypeError: If sys_id is not int/None or name is not string
        
    Examples:
        # Explicit ID (recommended for stable systems)
        SYS_NETWORK = add_system("NETWORK", 1)
        SYS_DATABASE = add_system("DATABASE", 2)
        
        # Auto-generated ID (useful for plugins/modules)
        SYS_PLUGIN = add_system("PLUGIN")
        
        # Use in logging
        logger.error("Connection failed", sys=SYS_NETWORK)
    
    Best Practices:
        - Use consistent ID ranges (e.g., core: 1-99, plugins: 100-199)
        - Define constants for frequently used systems
        - Document your system IDs in your project
    """
    # Validate name first
    if not name or not isinstance(name, str) or not name.strip():
        raise ValueError("System name must be a non-empty string")
    
    if sys_id is None:
        # Auto-generate ID: find highest existing ID and add 1
        if sys_map:
            # Get all numeric keys (in case there are non-int keys somehow)
            numeric_keys = [k for k in sys_map.keys() if isinstance(k, int)]
            sys_id = max(numeric_keys) + 1 if numeric_keys else 1
        else:
            sys_id = 1  # Start from 1 for user-defined systems (0 is SYS_GENERAL)
    else:
        # Validate provided sys_id
        if not isinstance(sys_id, int):
            raise TypeError("sys_id must be an integer or None")
        if sys_id < 0:
            raise ValueError("sys_id must be non-negative")
        if sys_id in sys_map:
            raise ValueError(f"System ID {sys_id} already exists")
    
    # Register the system
    sys_id = const(sys_id) if const else sys_id
    sys_map[sys_id] = const(name.strip()) if const else name.strip()
    return sys_id

def add_error(description, error_id=None):
    """Register a new error code for structured error reporting.
    
    Error codes enable:
    - Programmatic error handling based on numeric codes
    - Consistent error messages across the application  
    - Language-independent error identification
    - Efficient error analysis and metrics
    
    Args:
        description: Human-readable error description (str, required)
                     Should be concise but informative
        error_id: Unique error identifier (int or None, optional)
                  If None, automatically generates the next available ID
                     
    Returns:
        int: The error ID (const-wrapped if available) for use as a constant
        
    Raises:
        ValueError: If description is empty/whitespace or error_id already exists
        TypeError: If error_id is not int/None or description is not string
        
    Examples:
        # Network-related errors (100-199)
        ERROR_TIMEOUT = add_error("Connection timeout", 100)
        ERROR_DNS_FAIL = add_error("DNS resolution failed", 101)
        
        # Sensor errors (200-299)  
        ERROR_SENSOR_INIT = add_error("Sensor initialization failed", 200)
        ERROR_SENSOR_READ = add_error("Sensor read error")  # Auto ID
        
        # Use in logging
        logger.error("Network error", error_id=ERROR_TIMEOUT)
        
        # Programmatic handling
        if error_id == ERROR_TIMEOUT:
            retry_connection()
    
    Best Practices:
        - Group related errors in ID ranges
        - Keep descriptions concise (<50 chars)
        - Use present tense for descriptions
        - Consider i18n needs for user-facing errors
    """
    # Validate description first
    if not description or not isinstance(description, str) or not description.strip():
        raise ValueError("Error description must be a non-empty string")
    
    if error_id is None:
        # Auto-generate ID: find highest existing ID and add 1
        if errors_map:
            numeric_keys = [k for k in errors_map.keys() if isinstance(k, int)]
            error_id = max(numeric_keys) + 1 if numeric_keys else 1
        else:
            error_id = 1  # Start from 1 for user-defined errors (0 is ERROR_UNKNOWN)
    else:
        # Validate provided error_id
        if not isinstance(error_id, int):
            raise TypeError("error_id must be an integer or None")
        if error_id < 0:
            raise ValueError("error_id must be non-negative")
        if error_id in errors_map:
            raise ValueError(f"Error ID {error_id} already exists")
    
    # Register the error
    error_id = const(error_id) if const else error_id
    errors_map[error_id] = const(description.strip()) if const else description.strip()
    return error_id

# === BACKWARD COMPATIBILITY LAYER ===
# Automatically imports legacy user_defs.py if present, ensuring existing
# projects continue to work without modification.
#
# The legacy format expects:
# - Constants: SYS_* and ERROR_* (imported into global namespace)
# - Mappings: sys_map_user and errors_map_user dictionaries
#
# This compatibility layer will be maintained for the foreseeable future,
# but new projects should use the add_system() and add_error() API.

try:
    # Attempt to import the legacy user definitions module
    from logger import user_defs
    
    # Import all SYS_* and ERROR_* constants into global namespace
    # This preserves the ability to import them from defs:
    # Example: from logger.defs import SYS_CUSTOM
    for name in dir(user_defs):
        if name.startswith(('SYS_', 'ERROR_')):
            globals()[name] = getattr(user_defs, name)
    
    # Merge user-defined mappings into the global maps
    if hasattr(user_defs, 'sys_map_user'):
        sys_map.update(user_defs.sys_map_user)
    if hasattr(user_defs, 'errors_map_user'):
        errors_map.update(user_defs.errors_map_user)
        
except ImportError:
    # No user_defs.py present - expected for new projects
    # Continue with built-in definitions only
    pass
