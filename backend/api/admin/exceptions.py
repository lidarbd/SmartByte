"""
Custom exceptions for Admin API
"""

from fastapi import status


class AdminAPIError(Exception):
    """Base exception for all admin API errors."""
    
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MetricsCalculationError(AdminAPIError):
    """Raised when there's an error calculating system metrics."""
    
    def __init__(self, message: str = "Failed to calculate metrics"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class SessionNotFoundError(AdminAPIError):
    """Raised when a requested session doesn't exist."""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session with ID '{session_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class SessionQueryError(AdminAPIError):
    """Raised when there's an error querying sessions."""
    
    def __init__(self, message: str = "Failed to query sessions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class SessionDetailError(AdminAPIError):
    """Raised when there's an error retrieving session details."""
    
    def __init__(self, message: str = "Failed to retrieve session details"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class InvalidFileTypeError(AdminAPIError):
    """Raised when uploaded file is not a valid CSV."""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"Invalid file type. Expected CSV file, got: {filename}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class FileReadError(AdminAPIError):
    """Raised when there's an error reading the uploaded file."""
    
    def __init__(self, details: str):
        super().__init__(
            message=f"Failed to read uploaded file: {details}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CSVProcessingError(AdminAPIError):
    """Raised when there's an error processing the CSV file."""
    
    def __init__(self, details: str):
        super().__init__(
            message=f"Failed to process CSV file: {details}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ProductQueryError(AdminAPIError):
    """Raised when there's an error querying products from the database."""
    
    def __init__(self, message: str = "Failed to retrieve products"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )