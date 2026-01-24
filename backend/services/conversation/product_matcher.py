"""
Product Matcher Service

Filters and matches products based on customer requirements.

This is a critical component - it ensures the LLM only sees
products that actually match the customer's needs and are in stock.
"""

import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.db.conversation.models import Product
from backend.db.conversation.repositories import ProductRepository


class ProductMatcher:
    """
    Filters and matches products based on customer requirements.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
    
    def find_matching_products(
        self,
        customer_type: str,
        message: str,
        max_budget: Optional[float] = None,
        limit: int = 10
    ) -> List[Product]:
        """
        Find products that match customer requirements.
        
        Args:
            customer_type: Student, Engineer, Gamer, or Other
            message: User's message (to extract requirements)
            max_budget: Maximum price (extracted from message or conversation)
            limit: Maximum number of products to return
        
        Returns:
            List of matching Product objects
        
        Example:
            matcher = ProductMatcher(db)
            products = matcher.find_matching_products(
                customer_type="Student",
                message="I need a laptop for university, budget 3000 ILS",
                limit=5
            )
        """
        # Extract budget from message if not provided
        if max_budget is None:
            max_budget = self._extract_budget(message)
        
        # Determine product type preference
        product_type = self._extract_product_type(message)
        
        # Get base filtering criteria based on customer type
        filters = self._get_customer_filters(customer_type, message)
        
        # Add budget filter
        if max_budget:
            filters['max_price'] = max_budget
        
        # Add product type filter if specified
        if product_type:
            filters['product_type'] = product_type
        
        # Query database with filters
        products = self.repo.filter_products(**filters)
        
        # Additional filtering based on specs (for computers)
        if customer_type in ['Engineer', 'Gamer']:
            products = self._filter_by_specs(products, customer_type, message)
        
        # Return top matches (limit)
        return products[:limit]
    
    def _extract_budget(self, message: str) -> Optional[float]:
        """
        Extract budget from message using simple pattern matching.
        
        Examples:
        - "budget is 5000" → 5000
        - "up to 3000 shekels" → 3000
        - "around 4500" → 4500
        """
        # Pattern to match numbers (possibly with comma separators)
        patterns = [
            r'budget.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',  # "budget is 5,000"
            r'up to.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',   # "up to 3000"
            r'around.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',  # "around 4500"
            r'max.*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',     # "max 6000"
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:shekel|nis|ils)'  # "5000 shekels"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                # Remove commas and convert to float
                budget_str = match.group(1).replace(',', '')
                return float(budget_str)
        
        return None
    
    def _extract_product_type(self, message: str) -> Optional[str]:
        """
        Determine if user wants laptop or desktop.
        """
        message_lower = message.lower()
        
        if 'laptop' in message_lower or 'notebook' in message_lower or 'portable' in message_lower:
            return 'laptop'
        elif 'desktop' in message_lower or 'tower' in message_lower or 'pc' in message_lower:
            return 'desktop'
        
        return None
    
    def _get_customer_filters(self, customer_type: str, message: str) -> Dict[str, Any]:
        """
        Get filtering criteria based on customer type.
        """
        filters = {
            'min_stock': 1  # Always require items in stock
        }
        
        # Brand preference (optional)
        message_lower = message.lower()
        if 'lenovo' in message_lower:
            filters['brand'] = 'Lenovo'
        elif 'dell' in message_lower:
            filters['brand'] = 'Dell'
        
        return filters
    
    def _filter_by_specs(
        self,
        products: List[Product],
        customer_type: str,
        message: str
    ) -> List[Product]:
        """
        Additional filtering based on technical specs for Engineers and Gamers.
        """
        filtered = []
        message_lower = message.lower()
        
        for product in products:
            if not product.specs or not product.is_computer:
                continue
            
            # Engineer requirements
            if customer_type == 'Engineer':
                # Need good CPU and RAM
                ram = product.specs.get('ram_gb', 0)
                if ram >= 16:  # Engineers typically need 16GB+
                    filtered.append(product)
            
            # Gamer requirements
            elif customer_type == 'Gamer':
                # Need dedicated GPU
                gpu = product.specs.get('gpu', '').lower()
                if 'rtx' in gpu or 'radeon' in gpu or 'nvidia' in gpu:
                    filtered.append(product)
            
            else:
                filtered.append(product)
        
        return filtered if filtered else products