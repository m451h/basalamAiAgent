import requests
from langchain_core.tools import tool
from typing import Optional

api_url = "https://search.basalam.com/ai-engine/api/v2.0/product/search"

@tool
def search_basalam(query: str, max_price: Optional[int] = None, min_rating: Optional[float] = None, vendor_city: Optional[str] = None) -> list:
    """
    جستجوی تمیز و مرتب محصولات از باسلام
    فقط اطلاعات مهم هر محصول را برمی‌گرداند و بر اساس قیمت مرتب می‌کند.

    :param query: عبارت جستجو (مثلاً "کفش")
    :param max_price: حداکثر قیمت به تومان (مثلاً 500000)
    :param min_rating: حداقل امتیاز محصول (مثلاً 4.5)
    :param vendor_city: شهر فروشنده (مثلاً "تهران")
    :return: لیستی از محصولات با اطلاعات تمیز
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    params = {
        "q": query,
    }

    if max_price:
        params["max_price"] = max_price * 10  # Convert to Rial

    if min_rating:
        params["min_rating"] = min_rating
        
    if vendor_city:
        params["vendor_city"] = vendor_city

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        print("❌ پاسخ API:", response.status_code, response.text)
        raise Exception("خطا در جستجوی باسلام")

    all_data = response.json()
    products = all_data.get("products", [])

    cleaned_products = []

    for product in products:
        cleaned = {
            "name": product.get("name"),
            "price": int(product.get("price", 0)) // 10,
            "image": product.get("photo", {}).get("MEDIUM"),
            "rating": product.get("rating", {}).get("average"),
            "rating_count": product.get("rating", {}).get("count"),
            "vendor_name": product.get("vendor", {}).get("name"),
            "vendor_city": product.get("vendor", {}).get("owner", {}).get("city"),
            "product_id": product.get("id"),
            "link": f"https://basalam.com/p/{product.get('id')}",
        }
        
        # Apply filters
        if not cleaned["price"]:  # Skip products without price
            continue
        
        if min_rating and (not cleaned["rating"] or cleaned["rating"] < min_rating):
            continue
            
        if vendor_city and cleaned["vendor_city"] and cleaned["vendor_city"].lower() != vendor_city.lower():
            continue
            
        cleaned_products.append(cleaned)

    # مرتب‌سازی بر اساس قیمت
    sorted_products = sorted(cleaned_products, key=lambda x: x["price"])

    return sorted_products
