import logging
from abc import ABC, abstractmethod
from typing import List
from simu_core.exceptions import (
    SimuCoreException,
    ValidationException,
    SQLiteException,
    ParseException
)

logger = logging.getLogger(__name__)


class ErrorManager(ABC):
    """Abstract base class for error management."""
    
    def __init__(self):
        self.validation_errors: List[ValidationException] = []
        self.fatal_errors: List[SimuCoreException] = []
    
    def add_validation_error(self, error: ValidationException):
        """Add a non-fatal validation error to the list.
        
        These errors are collected and displayed together after
        the Read/Parse phase completes.
        """
        logger.warning(f"Validation error: {error.message}")
        self.validation_errors.append(error)
    
    def add_fatal_error(self, error: SimuCoreException):
        """Add a fatal error that will stop execution.
        
        Examples: SQLiteException, configuration errors.
        """
        logger.error(f"Fatal error: {str(error)}")
        self.fatal_errors.append(error)
    
    def has_validation_errors(self) -> bool:
        """Check if any validation errors were collected."""
        return len(self.validation_errors) > 0
    
    def has_fatal_errors(self) -> bool:
        """Check if any fatal errors occurred."""
        return len(self.fatal_errors) > 0
    
    def clear_validation_errors(self):
        """Clear all validation errors (used between phases)."""
        self.validation_errors.clear()
    
    @abstractmethod
    def display_errors(self):
        """Print errors to console in a readable format."""
        if self.has_fatal_errors():
            print("FATAL ERRORS - Simulation cannot continue:")
            for i, error in enumerate(self.fatal_errors, 1):
                print(f"\n{i}. {type(error).__name__}")
                print(f"   {str(error)}")
                if hasattr(error, 'cause') and error.cause:
                    print(f"   Caused by: {str(error.cause)}")
        
        if self.has_validation_errors():
            print(f"VALIDATION ERRORS ({len(self.validation_errors)} found):")
            for i, error in enumerate(self.validation_errors, 1):
                print(f"\n{i}. {error.message}")
                if error.field:
                    print(f"Field: {error.field}")