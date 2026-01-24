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

from backend.db.conversation.models import Product
from backend.db.conversation.repositories import ProductRepository


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
        max_upsell_price: float = 300
    ) -> Optional[Product]:
        """
        Select an appropriate accessory for upselling.
        
        Args:
            main_product: The main product being recommended
            customer_type: Type of customer
            max_upsell_price: Maximum price for upsell item
        
        Returns:
            Accessory Product or None if no suitable upsell found
        
        Example:
            selector = UpsellSelector(db)
            upsell = selector.select_upsell(
                main_product=laptop,
                customer_type="Student",
                max_upsell_price=200
            )
        """
        # Determine preferred accessory category
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