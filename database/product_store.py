
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

class ProductStore:
    def __init__(self, db_path: str = "database/products.db"):
        """Initialize the product store with SQLite database"""
        self.db_path = db_path
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Create the products table if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    product_id TEXT UNIQUE,
                    name TEXT,
                    price INTEGER,
                    image_url TEXT,
                    rating REAL,
                    rating_count INTEGER,
                    vendor_name TEXT,
                    vendor_city TEXT,
                    link TEXT,
                    description TEXT,
                    specifications TEXT,
                    reviews TEXT,
                    additional_images TEXT,
                    search_query TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Create index for faster searches
            conn.execute('CREATE INDEX IF NOT EXISTS idx_product_id ON products(product_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_search_query ON products(search_query)')
            conn.commit()
    
    def save_product(self, product_data: Dict[str, Any], search_query: str = "") -> str:
        """Save a product to the database and return the internal ID"""
        internal_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute('''
                    INSERT OR REPLACE INTO products (
                        id, product_id, name, price, image_url, rating, rating_count,
                        vendor_name, vendor_city, link, description, specifications,
                        reviews, additional_images, search_query, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    internal_id,
                    product_data.get('product_id', ''),
                    product_data.get('name', ''),
                    product_data.get('price', 0),
                    product_data.get('image', ''),
                    product_data.get('rating', 0.0),
                    product_data.get('rating_count', 0),
                    product_data.get('vendor_name', ''),
                    product_data.get('vendor_city', ''),
                    product_data.get('link', ''),
                    product_data.get('description', ''),
                    json.dumps(product_data.get('specifications', {}), ensure_ascii=False),
                    json.dumps(product_data.get('reviews', []), ensure_ascii=False),
                    json.dumps(product_data.get('additional_images', []), ensure_ascii=False),
                    search_query,
                    now,
                    now
                ))
                conn.commit()
                return internal_id
            except sqlite3.IntegrityError:
                # Product already exists, update it
                conn.execute('''
                    UPDATE products SET
                        name=?, price=?, image_url=?, rating=?, rating_count=?,
                        vendor_name=?, vendor_city=?, link=?, description=?,
                        specifications=?, reviews=?, additional_images=?,
                        search_query=?, updated_at=?
                    WHERE product_id=?
                ''', (
                    product_data.get('name', ''),
                    product_data.get('price', 0),
                    product_data.get('image', ''),
                    product_data.get('rating', 0.0),
                    product_data.get('rating_count', 0),
                    product_data.get('vendor_name', ''),
                    product_data.get('vendor_city', ''),
                    product_data.get('link', ''),
                    product_data.get('description', ''),
                    json.dumps(product_data.get('specifications', {}), ensure_ascii=False),
                    json.dumps(product_data.get('reviews', []), ensure_ascii=False),
                    json.dumps(product_data.get('additional_images', []), ensure_ascii=False),
                    search_query,
                    now,
                    product_data.get('product_id', '')
                ))
                # Return the existing internal ID
                cursor = conn.execute('SELECT id FROM products WHERE product_id=?', (product_data.get('product_id', ''),))
                result = cursor.fetchone()
                return result[0] if result else internal_id
    
    def get_product(self, internal_id: str) -> Optional[Dict[str, Any]]:
        """Get a product by its internal ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM products WHERE id=?', (internal_id,))
            row = cursor.fetchone()
            
            if row:
                product = dict(row)
                # Parse JSON fields
                product['specifications'] = json.loads(product['specifications']) if product['specifications'] else {}
                product['reviews'] = json.loads(product['reviews']) if product['reviews'] else []
                product['additional_images'] = json.loads(product['additional_images']) if product['additional_images'] else []
                return product
            return None
    
    def get_products_by_search(self, search_query: str) -> List[Dict[str, Any]]:
        """Get all products from a specific search query"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM products WHERE search_query=? ORDER BY created_at DESC', (search_query,))
            products = []
            for row in cursor.fetchall():
                product = dict(row)
                product['specifications'] = json.loads(product['specifications']) if product['specifications'] else {}
                product['reviews'] = json.loads(product['reviews']) if product['reviews'] else []
                product['additional_images'] = json.loads(product['additional_images']) if product['additional_images'] else []
                products.append(product)
            return products
    
    def get_all_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all stored products with a limit"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM products ORDER BY created_at DESC LIMIT ?', (limit,))
            products = []
            for row in cursor.fetchall():
                product = dict(row)
                product['specifications'] = json.loads(product['specifications']) if product['specifications'] else {}
                product['reviews'] = json.loads(product['reviews']) if product['reviews'] else []
                product['additional_images'] = json.loads(product['additional_images']) if product['additional_images'] else []
                products.append(product)
            return products
    
    def search_stored_products(self, query: str) -> List[Dict[str, Any]]:
        """Search through stored products by name or description"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM products 
                WHERE name LIKE ? OR description LIKE ? 
                ORDER BY created_at DESC
            ''', (f'%{query}%', f'%{query}%'))
            
            products = []
            for row in cursor.fetchall():
                product = dict(row)
                product['specifications'] = json.loads(product['specifications']) if product['specifications'] else {}
                product['reviews'] = json.loads(product['reviews']) if product['reviews'] else []
                product['additional_images'] = json.loads(product['additional_images']) if product['additional_images'] else []
                products.append(product)
            return products

    def delete_product(self, internal_id: str) -> bool:
        """Delete a product by its internal ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM products WHERE id=?', (internal_id,))
            conn.commit()
            return cursor.rowcount > 0
