"""
Conversation Services

This module contains all business logic related to customer conversations,
product recommendations, and customer type identification.
"""

from .csv_loader import CSVLoader
from .customer_identifier import CustomerIdentifier
from .product_matcher import ProductMatcher
from .upsell_selector import UpsellSelector
from .recommendation_service import RecommendationService
from .exceptions import (
    ServiceError,
    CSVParsingError,
    CustomerIdentificationError,
    ProductMatchingError,
    UpsellError,
    RecommendationError
)

__all__ = [
    'CSVLoader',
    'CustomerIdentifier',
    'ProductMatcher',
    'UpsellSelector',
    'RecommendationService',
    'ServiceError',
    'CSVParsingError',
    'CustomerIdentificationError',
    'ProductMatchingError',
    'UpsellError',
    'RecommendationError'
]
