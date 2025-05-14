import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def crawl_product_page(url: str) -> Dict[str, Any]:
    """
    Crawls a Basalam product page and extracts the name, price, and description.
    Returns a dictionary with extracted fields, or an error if failed.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        name = soup.select_one('h1.thh9OB')
        name_text = name.get_text(strip=True) if name else ''

        price = soup.select_one('span.PlpxQp')
        price_text = price.get_text(strip=True) if price else ''

        description = soup.select_one('p.fhJOs1.bs-read-more__text')
        description_text = description.get_text(strip=True) if description else ''

        return {
            'url': url,
            'name': name_text,
            'price': price_text,
            'description': description_text
        }
    except Exception as e:
        return {'error': str(e), 'url': url}

if __name__ == "__main__":
    test_url = "https://basalam.com/p/16078271"  # Replace with a real product URL
    import json
    result = crawl_product_page(test_url)
    print(json.dumps(result, ensure_ascii=False, indent=2))
