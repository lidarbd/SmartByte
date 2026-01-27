"""
Product Matcher Service

Filters and matches products based on customer requirements.

This is a critical component - it ensures the LLM only sees
products that actually match the customer's needs and are in stock.

FIXED VERSION: Added full Hebrew language support
"""

import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from db.conversation.models import Product
from db.conversation.repositories import ProductRepository


class ProductMatcher:
    """
    Filters and matches products based on customer requirements.

    Supports both English and Hebrew languages.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def find_matching_products(
        self,
        customer_type: str,
        message: str,
        max_budget: Optional[float] = None,
        product_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Product]:
        """
        Find products that match customer requirements.

        Args:
            customer_type: Student, Engineer, Gamer, or Other
            message: User's message (to extract requirements) - supports Hebrew and English
            max_budget: Maximum price (extracted from message or conversation)
            product_type: Product type preference from conversation history (laptop/desktop)
            category: Product category from conversation history (computer/mouse/keyboard/etc)
            limit: Maximum number of products to return

        Returns:
            List of matching Product objects

        Example:
            matcher = ProductMatcher(db)
            products = matcher.find_matching_products(
                customer_type="Student",
                message="אני סטודנט, צריך מחשב נייד, תקציב 3000 שקל",
                product_type="laptop",
                category="computer",
                limit=5
            )
        """
        print(f"FIND MATCHING PRODUCTS - Customer: {customer_type}, Message: '{message}'")

        # Extract budget from message if not provided
        if max_budget is None:
            max_budget = self._extract_budget(message)

        # Determine product type preference (use provided or extract from message)
        provided_product_type = product_type  # Remember if it was provided
        if product_type is None:
            product_type = self._extract_product_type(message)

        print(f"Product Type: {product_type} (from {'conversation history' if provided_product_type else 'current message' if product_type else 'not specified'})")

        # Get base filtering criteria based on customer type
        filters = self._get_customer_filters(customer_type, message)

        # Add category from conversation history if provided
        if category:
            filters['category'] = category
            print(f"Category from conversation history: {category}")

        # Add budget filter
        if max_budget:
            filters['max_price'] = max_budget

        # Add product type filter if specified
        if product_type:
            filters['product_type'] = product_type

        print(f"FILTERS: {filters}")

        # Query database with filters
        products = self.repo.filter_products(**filters)
        print(f"Found {len(products)} products")
        # Additional filtering based on specs (for computers)
        if customer_type in ['Engineer', 'Gamer']:
            products = self._filter_by_specs(products, customer_type, message)
            print(f"After specs: {len(products)} products")

        # Return top matches (limit)
        result = products[:limit]
        print(f"Returning {len(result)} products")
        if result:
            print(f"   First: {result[0].name} - {result[0].price} ILS")
        return result

    def _extract_budget(self, message: str) -> Optional[float]:
        """
        Extract budget from message using pattern matching.

        Supports both English and Hebrew.

        Examples:
        English:
        - "budget is 5000" → 5000
        - "up to 3000 shekels" → 3000
        - "around 4500" → 4500

        Hebrew:
        - "תקציב 3000" → 3000
        - "עד 5000 שקל" → 5000
        - "בסביבות 4000" → 4000
        """
        print(f"EXTRACTING BUDGET FROM MESSAGE: '{message}'")

        # Pattern to match numbers (with or without comma separators)
        patterns = [
            # English patterns
            r'budget.*?(\d{1,3}(?:,\d{3})+)',  # "budget is 5,000" (with commas)
            r'budget.*?(\d+)',  # "budget is 5000" (without commas)
            r'up to.*?(\d{1,3}(?:,\d{3})+)',   # "up to 3,000" (with commas)
            r'up to.*?(\d+)',   # "up to 3000" (without commas)
            r'around.*?(\d{1,3}(?:,\d{3})+)',  # "around 4,500" (with commas)
            r'around.*?(\d+)',  # "around 4500" (without commas)
            r'max.*?(\d{1,3}(?:,\d{3})+)',     # "max 6,000" (with commas)
            r'max.*?(\d+)',     # "max 6000" (without commas)
            r'(\d{1,3}(?:,\d{3})+)\s*(?:shekel|nis|ils)',  # "5,000 shekels" (with commas)
            r'(\d+)\s*(?:shekel|nis|ils)',  # "5000 shekels" (without commas)

            # Hebrew patterns
            r'תקציב.*?(\d{1,3}(?:,\d{3})+)',  # "תקציב 3,000" (with commas)
            r'תקציב.*?(\d+)',  # "תקציב 3000" (without commas)
            r'עד.*?(\d{1,3}(?:,\d{3})+)',     # "עד 5,000" (with commas)
            r'עד.*?(\d+)',     # "עד 5000" (without commas)
            r'בסביבות.*?(\d{1,3}(?:,\d{3})+)',  # "בסביבות 4,000" (with commas)
            r'בסביבות.*?(\d+)',  # "בסביבות 4000" (without commas)
            r'מקסימום.*?(\d{1,3}(?:,\d{3})+)',  # "מקסימום 6,000" (with commas)
            r'מקסימום.*?(\d+)',  # "מקסימום 6000" (without commas)
            r'מקסימלי.*?(\d{1,3}(?:,\d{3})+)',  # "מקסימלי 6,000" (with commas)
            r'מקסימלי.*?(\d+)',  # "מקסימלי 6000" (without commas)
            r'(\d{1,3}(?:,\d{3})+)\s*(?:שקל|ש"ח|שח)',  # "3,000 שקל" (with commas)
            r'(\d+)\s*(?:שקל|ש"ח|שח)',  # "3000 שקל" (without commas)
            r'(\d{1,3}(?:,\d{3})+)\s*₪',  # "3,000 ₪" (with commas)
            r'(\d+)\s*₪',  # "3000 ₪" (without commas)
        ]

        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                # Remove commas and convert to float
                budget_str = match.group(1).replace(',', '')
                budget = float(budget_str)
                print(f"BUDGET FOUND: Pattern '{pattern}' matched '{match.group(0)}' → Budget = {budget}")
                return budget

        print(f"NO BUDGET FOUND in message: '{message}'")
        return None

    def _extract_product_type(self, message: str) -> Optional[str]:
        """
        Determine if user wants laptop or desktop.

        Supports both English and Hebrew.
        """
        message_lower = message.lower()

        # Laptop keywords (English + Hebrew)
        laptop_keywords = [
            'laptop', 'notebook', 'portable',  # English
            'נייד', 'לפטופ', 'מחשב נייד', 'מחברת', 'ניידת'  # Hebrew
        ]

        # Desktop keywords (English + Hebrew)
        desktop_keywords = [
            'desktop', 'tower', 'pc',  # English
            'שולחני', 'מחשב שולחני', 'נייח', 'מגדל', 'דסקטופ'  # Hebrew
        ]

        # Check for laptop
        for keyword in laptop_keywords:
            if keyword in message_lower:
                return 'laptop'

        # Check for desktop
        for keyword in desktop_keywords:
            if keyword in message_lower:
                return 'desktop'

        return None

    def _get_customer_filters(self, customer_type: str, message: str) -> Dict[str, Any]:
        """
        Get filtering criteria based on customer type.

        Supports both English and Hebrew.
        """
        filters = {
            'min_stock': 1  # Always require items in stock
        }

        # Brand preference (works in both languages - brand names are the same)
        message_lower = message.lower()
        if 'lenovo' in message_lower:
            filters['brand'] = 'Lenovo'
        elif 'dell' in message_lower:
            filters['brand'] = 'Dell'

        # Check if user is looking for computers in general (Hebrew + English)
        computer_keywords = [
            'computer', 'computers', 'pc',  # English
            'מחשב', 'מחשבים', 'קומפיוטר'  # Hebrew
        ]
        if any(keyword in message_lower for keyword in computer_keywords):
            filters['category'] = 'computer'
            print(f"Computer keyword detected - adding category=computer filter")

        print(f"Customer filters generated: {filters}")
        return filters

    def _filter_by_specs(
        self,
        products: List[Product],
        customer_type: str,
        message: str
    ) -> List[Product]:
        """
        Additional filtering based on technical specs for Engineers and Gamers.

        Supports both English and Hebrew.
        """
        print(f"\nFILTERING BY SPECS:")
        print(f"   Customer Type: {customer_type}")
        print(f"   Products to filter: {len(products)}")

        filtered = []
        message_lower = message.lower()

        # Check if gaming is mentioned (English + Hebrew)
        gaming_keywords = [
            'gaming', 'gamer', 'game', 'games',  # English
            'גיימינג', 'גיימר', 'משחקים', 'משחק'  # Hebrew
        ]
        is_gaming_mentioned = any(keyword in message_lower for keyword in gaming_keywords)
        print(f"   Gaming mentioned: {is_gaming_mentioned}")

        for product in products:
            print(f"\n   Checking product: {product.name}")
            print(f"   - Has specs: {bool(product.specs)}")
            print(f"   - Is computer: {product.is_computer}")

            if not product.specs or not product.is_computer:
                print(f"   - SKIPPED (no specs or not computer)")
                continue

            # Engineer requirements
            if customer_type == 'Engineer':
                # Need good CPU and RAM
                ram = product.specs.get('ram_gb', 0)
                print(f"   - RAM: {ram}GB (need 16GB+)")
                if ram >= 16:  # Engineers typically need 16GB+
                    print(f"   - PASSED (enough RAM)")
                    filtered.append(product)
                else:
                    print(f"   - FAILED (not enough RAM)")

            # Gamer requirements OR gaming mentioned in message
            elif customer_type == 'Gamer' or is_gaming_mentioned:
                # Need dedicated GPU
                gpu = product.specs.get('gpu', '').lower()
                print(f"   - GPU: {gpu}")

                if any(word in gpu for word in ['vega', 'uhd', 'iris']):
                    print(f"   - FAILED (integrated graphics: {gpu})")
                    continue
                if 'rtx' in gpu or 'radeon' in gpu or 'nvidia' in gpu or 'geforce' in gpu:
                    print(f"   - PASSED (dedicated GPU)")
                    filtered.append(product)
                else:
                    print(f"   - FAILED (no dedicated GPU keywords found)")

            else:
                print(f"   - PASSED (no special requirements)")
                filtered.append(product)

        print(f"\n   Products passed filter: {len(filtered)}")

        if not filtered:
            print(f"   WARNING: No products passed specs filter for {customer_type}")
            print(f"   Returning empty list (no suitable products)")
            return []

        print(f"   Returning {len(filtered)} filtered products")
        return filtered
