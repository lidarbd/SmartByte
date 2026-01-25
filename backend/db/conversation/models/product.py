"""
Product Model

Represents products in the computer store.
Products can be computers (laptops/desktops) or accessories (mouse, monitor, bag, etc.)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime, timezone
from .base import Base


class Product(Base):
    """
    Represents a product in the computer store.
    Can be a computer (laptop/desktop) or an accessory (mouse, monitor, bag, etc.)
    
    Attributes:
        id: Unique internal identifier (auto-generated)
        sku: Stock Keeping Unit - unique product identifier from CSV
        name: Product name (model for computers, product_name for accessories)
        brand: Manufacturer (Lenovo, Dell, HP, etc.)
        product_type: Type of product (laptop, desktop, accessory)
        category: Subcategory (computer, keyboard, mouse, headset, bag, etc.)
        price: Price in ILS (Israeli Shekels)
        stock: Current stock quantity (0 means out of stock)
        specs: Technical specifications stored as JSON
               For computers: cpu, gpu, ram_gb, storage_gb, os, warranty_years
               For accessories: can be empty or contain relevant specs
        description: General product description (optional, can be generated from specs)
        created_at: When the product was added to the system
        updated_at: When the product was last modified
    """
    __tablename__ = 'products'
    
    # Primary key - uniquely identifies each product internally
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # SKU - Stock Keeping Unit from CSV (unique product code)
    # Example: LAP-LNV-001, ACC-DLL-003
    sku = Column(String(50), unique=True, nullable=False, index=True)
    
    # Product name - cannot be null
    # For computers: model (e.g., "ThinkPad X1 Carbon Gen 10")
    # For accessories: product_name (e.g., "Dell KB216 Wired Keyboard")
    name = Column(String(255), nullable=False)
    
    # Brand/Manufacturer
    brand = Column(String(100), nullable=False, index=True)
    
    # Product type - high-level category
    # Values: "laptop", "desktop", "accessory"
    product_type = Column(String(50), nullable=False, index=True)
    
    # Category - more specific classification
    # For computers: usually "computer"
    # For accessories: "keyboard", "mouse", "headset", "bag", etc.
    category = Column(String(100), nullable=False, index=True)
    
    # Price with index for faster filtering by budget
    price = Column(Float, nullable=False, index=True)
    
    # Stock quantity with index (we'll frequently check availability)
    stock = Column(Integer, nullable=False, default=0, index=True)
    
    # Specs stored as JSON for flexibility
    # For computers, will contain:
    # {
    #   "cpu": "Intel i7-1260P",
    #   "gpu": "Intel Iris Xe",
    #   "ram_gb": 32,
    #   "storage_gb": 1024,
    #   "os": "Windows 11 Pro",
    #   "warranty_years": 3
    # }
    # For accessories, might be empty {} or contain relevant specs
    specs = Column(JSON, nullable=True)
    
    # Text description - can be generated from specs or added manually
    description = Column(Text, nullable=True)
    
    # Timestamps for tracking when products are added/modified
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """
        String representation of the Product object.
        Useful for debugging - when we print a product, we see meaningful info.
        """
        return f"<Product(sku='{self.sku}', name='{self.name}', brand='{self.brand}', price={self.price}, stock={self.stock})>"
    
    def to_dict(self) -> dict:
        """
        Convert Product to dictionary for easy JSON serialization.
        Useful for API responses.
        """
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "brand": self.brand,
            "product_type": self.product_type,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "specs": self.specs or {},
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def is_computer(self) -> bool:
        """Check if this product is a computer (laptop or desktop)."""
        return self.product_type in ['laptop', 'desktop']
    
    @property
    def is_accessory(self) -> bool:
        """Check if this product is an accessory."""
        return self.product_type == 'accessory'
    
    @property
    def display_name(self) -> str:
        """
        Get a full display name including brand.
        Example: "Lenovo ThinkPad X1 Carbon Gen 10"
        """
        return f"{self.brand} {self.name}"