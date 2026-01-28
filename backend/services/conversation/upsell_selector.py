"""
Upsell Selector Service

Selects relevant accessory for upsell based on the recommended product.

Upsell rules:
- Laptop → Wireless mouse, laptop bag, or headset
- Desktop → Wired keyboard/mouse combo, or monitor
- For students → Cheaper accessories
- For gamers → Gaming accessories (RGB mouse, gaming headset)
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from db.conversation.models import Product
from db.conversation.repositories import ProductRepository


class UpsellSelector:
    """
    Selects relevant accessory for upsell based on the recommended product.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
    
    def select_upsell(
        self,
        main_product: Product,
        customer_type: str,
        conversation_history: Optional[List] = None,
        max_upsell_price: float = 300,
        requested_accessory: Optional[str] = None
    ) -> Optional[Product]:
        """
        Select an appropriate accessory for upselling.

        Args:
            main_product: The main product being recommended
            customer_type: Type of customer
            conversation_history: Full conversation history to detect explicit accessory requests
            max_upsell_price: Maximum price for upsell item
            requested_accessory: Explicitly requested accessory category (e.g., 'headset', 'mouse')

        Returns:
            Accessory Product or None if no suitable upsell found

        Example:
            selector = UpsellSelector(db)
            upsell = selector.select_upsell(
                main_product=laptop,
                customer_type="Student",
                requested_accessory="headset",
                max_upsell_price=1500
            )
        """
        # Highest priority: Use explicitly requested accessory if provided
        if requested_accessory:
            print(f"User explicitly requested {requested_accessory} accessory (budget: {max_upsell_price})")
            accessories = self.repo.filter_products(
                product_type='accessory',
                category=requested_accessory,
                max_price=max_upsell_price,
                min_stock=1
            )
            if accessories:
                return accessories[0]
            else:
                print(f"No {requested_accessory} found within budget {max_upsell_price}")

        # Second priority: Check conversation history for implicit requests
        if conversation_history:
            explicit_category = self._detect_explicit_accessory_request(conversation_history)
            if explicit_category:
                print(f"Detected {explicit_category} accessory from conversation")
                accessories = self.repo.filter_products(
                    product_type='accessory',
                    category=explicit_category,
                    max_price=max_upsell_price,
                    min_stock=1
                )
                if accessories:
                    return accessories[0]

        # Third priority: Determine preferred accessory category based on product/customer type
        preferred_categories = self._get_preferred_categories(
            main_product,
            customer_type
        )

        # Find accessories in preferred categories
        for category in preferred_categories:
            accessories = self.repo.filter_products(
                product_type='accessory',
                category=category,
                max_price=max_upsell_price,
                min_stock=1
            )

            if accessories:
                # Return the first match (already sorted by price)
                return accessories[0]

        # If no specific match, try any accessory
        generic_accessories = self.repo.filter_products(
            product_type='accessory',
            max_price=max_upsell_price,
            min_stock=1
        )

        return generic_accessories[0] if generic_accessories else None
    
    def _detect_explicit_accessory_request(self, conversation_history: List) -> Optional[str]:
        """
        Detect if user explicitly requested a specific accessory category in any message.

        Args:
            conversation_history: List of conversation messages with 'role' and 'content'

        Returns:
            Accessory category if detected, None otherwise
        """
        # Accessory keywords mapping
        accessory_keywords = {
            'headset': ['headset', 'headphones', 'earphones', 'אוזניות', 'אזניות'],
            'mouse': ['mouse', 'עכבר', 'עכברים'],
            'keyboard': ['keyboard', 'מקלדת'],
            'monitor': ['monitor', 'screen', 'display', 'מסך', 'צג'],
            'bag': ['bag', 'backpack', 'תיק', 'תרמיל']
        }

        # Check all user messages in conversation history
        for message in conversation_history:
            if message.get('role') == 'user':
                message_lower = message.get('content', '').lower()

                # Check each category
                for category, keywords in accessory_keywords.items():
                    if any(keyword in message_lower for keyword in keywords):
                        return category

        return None

    def _get_preferred_categories(
        self,
        main_product: Product,
        customer_type: str
    ) -> List[str]:
        """
        Determine which accessory categories are most relevant.
        """
        categories = []

        # Based on main product type
        if main_product.product_type == 'laptop':
            categories.extend(['mouse', 'bag', 'headset'])
        elif main_product.product_type == 'desktop':
            categories.extend(['keyboard', 'mouse', 'headset'])

        # Based on customer type
        if customer_type == 'Gamer':
            # Prefer gaming accessories
            categories.insert(0, 'mouse')  # Gaming mice first
            categories.insert(1, 'headset')
        elif customer_type == 'Student':
            # Prefer budget-friendly accessories
            categories.insert(0, 'mouse')  # Basic mouse is useful
            categories.insert(1, 'bag')    # Bag for portability

        return categories