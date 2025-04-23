import requests
from langchain_core.tools import tool
from typing import Optional

api_url = "https://search.basalam.com/ai-engine/api/v2.0/product/search"

@tool
def search_basalam(query: str, max_price: Optional[int] = None) -> list:
    """
    جستجوی تمیز و مرتب محصولات از باسلام
    فقط اطلاعات مهم هر محصول را برمی‌گرداند و بر اساس قیمت مرتب می‌کند.

    :param query: عبارت جستجو (مثلاً "کفش")
    :param max_price: حداکثر قیمت به تومان (مثلاً 500000)
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
        params["max_price"] = max_price

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
        if cleaned["price"]:  # فقط محصولاتی که قیمت دارند
            cleaned_products.append(cleaned)

    # مرتب‌سازی بر اساس قیمت
    sorted_products = sorted(cleaned_products, key=lambda x: x["price"])

    return sorted_products
