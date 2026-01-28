"""
Repository Pattern for Database Operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.conversation.models import Product, ChatSession, ChatMessage, Recommendation
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


class ProductRepository:
    """
    Repository for Product-related database operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, product_data: Dict[str, Any]) -> Product:
        """
        Create a new product in the database.
        
        Args:
            product_data: Dictionary containing product information
                         Required: sku, name, brand, product_type, category, price, stock
                         Optional: specs, description
        """
        product = Product(**product_data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Retrieve a single product by its internal ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """
        Retrieve a single product by its SKU.
        
        Args:
            sku: Stock Keeping Unit (e.g., "LAP-LNV-001")
        """
        return self.db.query(Product).filter(Product.sku == sku).first()
    
    def get_all_products(self) -> List[Product]:
        """Retrieve all products from the database."""
        return self.db.query(Product).all()
    
    def filter_products(
        self,
        product_type: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        min_stock: int = 1,
        min_ram: Optional[int] = None,
        min_storage: Optional[int] = None
    ) -> List[Product]:
        """
        Filter products based on multiple criteria.
        
        This is the core function for finding products that match customer needs.
        
        Args:
            product_type: Type filter ("laptop", "desktop", "accessory")
            category: Category filter ("computer", "keyboard", "mouse", etc.)
            brand: Brand filter ("Lenovo", "Dell", etc.)
            max_price: Maximum price customer is willing to pay
            min_price: Minimum price (useful for filtering out very cheap options)
            min_stock: Minimum stock quantity (default 1 = must be available)
            min_ram: Minimum RAM in GB (for computers only)
            min_storage: Minimum storage in GB (for computers only)
        
        Returns:
            List of products matching all criteria, sorted by price
        
        Examples:
            # Find all Lenovo laptops under 5000 ILS in stock
            filter_products(product_type="laptop", brand="Lenovo", max_price=5000)
            
            # Find all gaming desktops with at least 16GB RAM and RTX GPU
            filter_products(product_type="desktop", min_ram=16, category="computer")
        """
        query = self.db.query(Product)

        print(f"[ProductRepository] Filtering with: product_type={product_type}, category={category}, brand={brand}, max_price={max_price}, min_stock={min_stock}")

        # Filter by product type
        if product_type:
            query = query.filter(Product.product_type == product_type)
            print(f"[ProductRepository] Added product_type filter: {product_type}")

        # Filter by category
        if category:
            query = query.filter(Product.category == category)
            print(f"[ProductRepository] Added category filter: {category}")
        
        # Filter by brand
        if brand:
            query = query.filter(Product.brand == brand)
        
        # Price range filters
        if max_price:
            query = query.filter(Product.price <= max_price)
        if min_price:
            query = query.filter(Product.price >= min_price)
        
        # Stock filter - always applied (we don't recommend out-of-stock items)
        query = query.filter(Product.stock >= min_stock)
        
        # Get results
        results = query.all()
        print(f"[ProductRepository] Found {len(results)} products after DB query")
        if results and len(results) > 0:
            print(f"[ProductRepository] First result: {results[0].name} | Category: {results[0].category} | Price: {results[0].price}")

        # Additional filtering based on specs (for computers)
        if min_ram or min_storage:
            filtered_results = []
            for product in results:
                if product.specs:
                    # Check RAM requirement
                    if min_ram and product.specs.get('ram_gb', 0) < min_ram:
                        continue
                    # Check storage requirement
                    if min_storage and product.specs.get('storage_gb', 0) < min_storage:
                        continue
                    filtered_results.append(product)
            results = filtered_results
        
        # Sort by price (cheapest first)
        results.sort(key=lambda p: p.price)
        
        return results
    
    def search_products(self, search_term: str) -> List[Product]:
        """
        Search products by name, brand, or SKU.
        
        Args:
            search_term: Text to search for (case-insensitive)
        
        Returns:
            List of matching products
        """
        search_pattern = f"%{search_term}%"
        return self.db.query(Product).filter(
            or_(
                Product.name.ilike(search_pattern),
                Product.brand.ilike(search_pattern),
                Product.sku.ilike(search_pattern)
            )
        ).all()
    
    def get_computers_by_specs(
        self,
        min_ram: Optional[int] = None,
        gpu_contains: Optional[str] = None
    ) -> List[Product]:
        """
        Find computers with specific technical specs.
        
        Args:
            min_ram: Minimum RAM in GB
            gpu_contains: Text that should appear in GPU name (e.g., "RTX" for gaming)
        
        Returns:
            List of computers matching specs
        """
        # Get all computers
        computers = self.db.query(Product).filter(
            or_(Product.product_type == 'laptop', Product.product_type == 'desktop')
        ).all()
        
        # Filter by specs
        results = []
        for computer in computers:
            if not computer.specs:
                continue
            
            # Check RAM
            if min_ram and computer.specs.get('ram_gb', 0) < min_ram:
                continue
            
            # Check GPU
            if gpu_contains:
                gpu = computer.specs.get('gpu', '').lower()
                if gpu_contains.lower() not in gpu:
                    continue
            
            results.append(computer)
        
        return results
    
    def update_stock(self, product_id: int, new_stock: int) -> Optional[Product]:
        """Update the stock quantity for a product."""
        product = self.get_product_by_id(product_id)
        if product:
            product.stock = new_stock
            product.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(product)
        return product
    
    def delete_all_products(self):
        """
        Delete all products from the database.
        WARNING: This is destructive and cannot be undone!
        """
        self.db.query(Product).delete()
        self.db.commit()
    
    def bulk_create_products(self, products_data: List[Dict[str, Any]]) -> int:
        """
        Create multiple products in a single database transaction.
        
        This is MUCH faster than calling create_product() in a loop.
        
        Args:
            products_data: List of dictionaries, each containing product info
        
        Returns:
            Number of products created
        """
        products = [Product(**data) for data in products_data]
        self.db.bulk_save_objects(products)
        self.db.commit()
        return len(products)
    
    def upsert_product(self, product_data: Dict[str, Any]) -> Product:
        """
        Create a product or update if SKU already exists.
        
        Useful when loading CSV files repeatedly - won't create duplicates.
        
        Args:
            product_data: Dictionary with product information (must include 'sku')
        
        Returns:
            The created or updated Product
        """
        sku = product_data.get('sku')
        if not sku:
            raise ValueError("SKU is required for upsert operation")
        
        # Try to find existing product
        existing = self.get_product_by_sku(sku)
        
        if existing:
            # Update existing product
            for key, value in product_data.items():
                if key != 'sku':  # Don't update SKU
                    setattr(existing, key, value)
            existing.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new product
            return self.create_product(product_data)
        
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[Product]:
        """
        Update an existing product with new data.
        
        Args:
            product_id: Internal ID of the product to update
            product_data: Dictionary with updated product information
        
        Returns:
            The updated Product object or None if not found
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        
        # Update all provided fields
        for key, value in product_data.items():
            if key != 'id':  # Don't update the ID itself
                setattr(product, key, value)
        
        product.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(product)
        return product


class ChatSessionRepository:
    """Repository for ChatSession operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, session_id: str) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(session_id=session_id, started_at=datetime.now(timezone.utc))
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a session by its external ID."""
        return self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    
    def update_customer_type(self, session_id: str, customer_type: str) -> Optional[ChatSession]:
        """Update the customer type after identification."""
        session = self.get_session_by_id(session_id)
        if session:
            session.customer_type = customer_type
            self.db.commit()
            self.db.refresh(session)
        return session
    
    def get_all_sessions(self, limit: int = 100) -> List[ChatSession]:
        """Retrieve recent sessions (for admin dashboard)."""
        return self.db.query(ChatSession).order_by(ChatSession.started_at.desc()).limit(limit).all()


class ChatMessageRepository:
    """Repository for ChatMessage operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        """Save a new message to the database."""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_session_messages(self, session_id: int) -> List[ChatMessage]:
        """Retrieve all messages for a session in chronological order."""
        return self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.asc()).all()


class RecommendationRepository:
    """Repository for Recommendation operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_recommendation(
        self,
        session_id: int,
        product_id: int,
        recommendation_text: str,
        upsell_product_id: Optional[int] = None
    ) -> Recommendation:
        """Save a new recommendation."""
        recommendation = Recommendation(
            session_id=session_id,
            product_id=product_id,
            upsell_product_id=upsell_product_id,
            recommendation_text=recommendation_text,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation
    
    def get_session_recommendations(self, session_id: int) -> List[Recommendation]:
        """Retrieve all recommendations made in a session."""
        return self.db.query(Recommendation).filter(
            Recommendation.session_id == session_id
        ).all()