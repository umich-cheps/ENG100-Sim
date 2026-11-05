class SimuCoreException(Exception):
    """Base exception for all SimuCore errors."""
    pass


class ValidationException(SimuCoreException):
    """Raised when input validation fails.
    
    These errors should be collected and displayed together,
    not stop execution immediately.
    """
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.message = message
        self.field = field  # Which field/parameter failed validation


class SQLiteException(SimuCoreException):
    """Raised when SQLite database operations fail.
    
    These are fatal errors that stop execution immediately.
    """
    def __init__(self, error: str, cause: Exception = None):
        super().__init__(error)
        self.error = error
        self.cause = cause  # Original exception


class ConfigurationException(SimuCoreException):
    """Raised when required configuration is missing or invalid."""
    pass

class FunctionNotFoundError(SimuCoreException):
    """Raised when a required function is not defined."""
    pass