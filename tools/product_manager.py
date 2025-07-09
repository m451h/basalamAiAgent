
from langchain_core.tools import tool
from typing import Dict, List, Any, Optional
from database.product_store import ProductStore

# Initialize the product store
product_store = ProductStore()

@tool
def save_product_details(product_data: Dict[str, Any], search_query: str = "") -> str:
    """
    Save detailed product information to local storage.
    Returns the internal ID of the saved product.
    
    Args:
        product_data: Dictionary containing product information
        search_query: The original search query that found this product
    
    Returns:
        Internal ID of the saved product
    """
    try:
        internal_id = product_store.save_product(product_data, search_query)
        return f"محصول با موفقیت ذخیره شد. شناسه: {internal_id}"
    except Exception as e:
        return f"خطا در ذخیره محصول: {str(e)}"

@tool
def get_product_details(internal_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed product information by internal ID.
    
    Args:
        internal_id: The internal ID of the product
    
    Returns:
        Product details or None if not found
    """
    try:
        product = product_store.get_product(internal_id)
        if product:
            return product
        else:
            return {"error": "محصول پیدا نشد"}
    except Exception as e:
        return {"error": f"خطا در دریافت اطلاعات محصول: {str(e)}"}

@tool
def search_saved_products(query: str) -> List[Dict[str, Any]]:
    """
    Search through saved products by name or description.
    
    Args:
        query: Search term to look for in product names and descriptions
    
    Returns:
        List of matching products
    """
    try:
        products = product_store.search_stored_products(query)
        return products
    except Exception as e:
        return [{"error": f"خطا در جستجوی محصولات ذخیره شده: {str(e)}"}]

@tool
def get_recent_products(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recently viewed/saved products.
    
    Args:
        limit: Maximum number of products to return
    
    Returns:
        List of recent products
    """
    try:
        products = product_store.get_all_products(limit)
        return products
    except Exception as e:
        return [{"error": f"خطا در دریافت محصولات اخیر: {str(e)}"}]

@tool
def compare_products(product_ids: List[str]) -> Dict[str, Any]:
    """
    Compare multiple products by their internal IDs.
    
    Args:
        product_ids: List of internal product IDs to compare
    
    Returns:
        Comparison data for the products
    """
    try:
        products = []
        for pid in product_ids:
            product = product_store.get_product(pid)
            if product:
                products.append(product)
        
        if len(products) < 2:
            return {"error": "حداقل دو محصول برای مقایسه نیاز است"}
        
        comparison = {
            "products": products,
            "comparison": {
                "prices": [p['price'] for p in products],
                "ratings": [p['rating'] for p in products],
                "vendors": [p['vendor_name'] for p in products],
                "cities": [p['vendor_city'] for p in products]
            }
        }
        
        return comparison
    except Exception as e:
        return {"error": f"خطا در مقایسه محصولات: {str(e)}"}
