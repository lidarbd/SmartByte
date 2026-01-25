"""
CSV Loader Service

Handles loading products from CSV files into the database.
"""

import csv
import io
from typing import Dict, Any
from sqlalchemy.orm import Session

from db.conversation.repositories import ProductRepository
from .exceptions import CSVParsingError


class CSVLoader:
    """
    Handles loading products from CSV files into the database.
    
    Expected CSV formats:
    - Computers: sku, brand, model, product_type, category, stock, price, cpu, gpu, ram_gb, storage_gb, os, warranty_years
    - Accessories: sku, brand, product_name, product_type, category, stock, price
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
    
    def load_from_csv(self, file_path: str, clear_existing: bool = False) -> Dict[str, Any]:
        """
        Load products from a CSV file on disk.
        
        Args:
            file_path: Path to CSV file
            clear_existing: If True, delete all existing products before loading
        
        Returns:
            Dictionary with loading statistics:
            {
                "total_rows": 100,
                "loaded": 95,
                "skipped": 5,
                "errors": ["row 3: missing price", ...]
            }
        
        Raises:
            CSVParsingError: If CSV cannot be read
        """
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            
            # Use the shared processing logic
            return self._process_csv_content(
                file_content=file_content,
                clear_existing=clear_existing,
                upsert=False
            )
        
        except FileNotFoundError:
            raise CSVParsingError(f"CSV file not found: {file_path}")
        
        except Exception as e:
            raise CSVParsingError(f"Failed to load CSV: {str(e)}")
    
    def load_from_upload(self, file_content: str, upsert: bool = False) -> Dict[str, Any]:
        """
        Load products from uploaded CSV content (already in memory).
        
        This method is designed for API uploads where the file content
        is already read into memory as a string.
        
        Args:
            file_content: CSV content as string
            upsert: If True, update existing products with same SKU.
                   If False, skip products with existing SKUs.
        
        Returns:
            Dictionary with loading statistics:
            {
                "total_rows": 100,
                "loaded": 95,
                "updated": 5,  # Only if upsert=True
                "skipped": 5,
                "errors": ["row 3: missing price", ...]
            }
        
        Raises:
            CSVParsingError: If CSV cannot be parsed
        """
        return self._process_csv_content(
            file_content=file_content,
            clear_existing=False,
            upsert=upsert
        )
    
    def _process_csv_content(
        self, 
        file_content: str, 
        clear_existing: bool = False,
        upsert: bool = False
    ) -> Dict[str, Any]:
        """
        Core logic for processing CSV content.
        
        This method contains the shared logic used by both load_from_csv
        and load_from_upload, avoiding code duplication.
        
        Args:
            file_content: CSV content as string
            clear_existing: If True, delete all existing products before loading
            upsert: If True, update existing products; if False, skip them
        
        Returns:
            Dictionary with loading statistics
        """
        stats = {
            "total_rows": 0,
            "loaded": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }
        
        try:
            # Clear existing products if requested
            if clear_existing:
                self.repo.delete_all_products()
                print("Cleared all existing products")
            
            # Use StringIO to read CSV from string (works for both file and upload)
            csv_file = io.StringIO(file_content)
            csv_reader = csv.DictReader(csv_file)
            
            # Process each row
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
                stats["total_rows"] += 1
                
                try:
                    # Parse and validate row
                    product_data = self._parse_csv_row(row)
                    
                    # Check if product with this SKU already exists
                    existing_product = self.repo.get_product_by_sku(product_data['sku'])
                    
                    if existing_product:
                        if upsert:
                            # Update existing product
                            self.repo.update_product(existing_product.id, product_data)
                            stats["updated"] += 1
                        else:
                            # Skip this product
                            stats["skipped"] += 1
                            stats["errors"].append(
                                f"Row {row_num}: Product with SKU '{product_data['sku']}' already exists (skipped)"
                            )
                    else:
                        # Create new product
                        self.repo.create_product(product_data)
                        stats["loaded"] += 1
                
                except Exception as e:
                    stats["skipped"] += 1
                    stats["errors"].append(f"Row {row_num}: {str(e)}")
            
            # Commit all changes
            self.db.commit()
            print(f"Processed {stats['total_rows']} rows: {stats['loaded']} loaded, {stats['updated']} updated, {stats['skipped']} skipped")
            
            return stats
        
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            raise CSVParsingError(f"Failed to process CSV: {str(e)}")
    
    def _parse_csv_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse a single CSV row and convert it to Product data.
        
        Since CSV structure is known and fixed, we access fields directly.
        If a required field is missing, Python will raise KeyError automatically.
        
        Args:
            row: Dictionary from CSV reader
        
        Returns:
            Dictionary ready for Product creation
        
        Raises:
            KeyError: If required field is missing
            ValueError: If field value is invalid
        """
        # Extract basic fields (will raise KeyError if missing)
        sku = row['sku'].strip()
        brand = row['brand'].strip()
        product_type = row['product_type'].strip()
        category = row['category'].strip()
        
        # Parse numeric fields
        try:
            price = float(row['price'])
            stock = int(row['stock'])
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid price or stock value: {str(e)}")
        
        # Determine product name - flexible approach that works for any product type
        if 'model' in row and row['model'].strip():
            name = row['model'].strip()
        elif 'product_name' in row and row['product_name'].strip():
            name = row['product_name'].strip()
        else:
            raise ValueError("Product must have either 'model' or 'product_name' field")
        
        # Build specs dictionary for products that have technical specs
        specs = self._extract_specs(row)
        
        # Create product data dictionary
        product_data = {
            'sku': sku,
            'name': name,
            'brand': brand,
            'product_type': product_type,
            'category': category,
            'price': price,
            'stock': stock,
            'specs': specs if specs else None,
            'description': self._generate_description(name, brand, specs)
        }
        
        return product_data
    
    def _extract_specs(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract technical specs from row if they exist.
        
        This method is flexible - it checks which spec fields are present
        rather than assuming based on product type.
        
        Args:
            row: CSV row data
        
        Returns:
            Dictionary of specs, or empty dict if no specs present
        """
        specs = {}
        
        # List of possible spec fields
        spec_fields = {
            'cpu': str,
            'gpu': str,
            'ram_gb': int,
            'storage_gb': int,
            'os': str,
            'warranty_years': int
        }
        
        # Extract each spec field if it exists and has a value
        for field, field_type in spec_fields.items():
            if field in row and row[field].strip():
                try:
                    if field_type == int:
                        specs[field] = int(row[field])
                    else:
                        specs[field] = row[field].strip()
                except ValueError:
                    # If conversion fails, skip this field
                    pass
        
        return specs
    
    def _generate_description(self, name: str, brand: str, specs: Dict[str, Any]) -> str:
        """
        Generate a basic description from product specs.
        
        This is useful for search and display purposes.
        """
        if not specs:
            return f"{brand} {name}"
        
        parts = [f"{brand} {name}"]
        
        if specs.get('cpu'):
            parts.append(f"CPU: {specs['cpu']}")
        if specs.get('ram_gb'):
            parts.append(f"RAM: {specs['ram_gb']}GB")
        if specs.get('storage_gb'):
            parts.append(f"Storage: {specs['storage_gb']}GB")
        if specs.get('gpu'):
            parts.append(f"GPU: {specs['gpu']}")
        
        return " | ".join(parts)