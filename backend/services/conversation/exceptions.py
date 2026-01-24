"""
Custom Exceptions for Services Layer

These exceptions allow us to handle specific business logic errors
in a clean and consistent way.
"""

class ServiceError(Exception):
    """Base exception for all service-related errors"""
    pass


class CSVParsingError(ServiceError):
    """Raised when CSV file cannot be parsed or contains invalid data"""
    pass


class CustomerIdentificationError(ServiceError):
    """Raised when customer type cannot be identified"""
    pass


class ProductMatchingError(ServiceError):
    """Raised when no products match the customer's requirements"""
    pass


class UpsellError(ServiceError):
    """Raised when upsell product selection fails"""
    pass


class RecommendationError(ServiceError):
    """Raised when recommendation generation fails"""
    pass