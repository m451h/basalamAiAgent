
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from langchain_core.tools import tool
import re

@tool
def crawl_product_page(url: str) -> Dict[str, Any]:
    """
    Crawls a Basalam product page and extracts comprehensive product information.
    Returns a dictionary with all available product details.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract basic info
        name = soup.select_one('h1.thh9OB')
        name_text = name.get_text(strip=True) if name else ''

        price = soup.select_one('span.PlpxQp')
        price_text = price.get_text(strip=True) if price else ''
        
        # Extract numeric price
        price_numeric = 0
        if price_text:
            price_numbers = re.findall(r'[\d,]+', price_text.replace(',', ''))
            if price_numbers:
                price_numeric = int(price_numbers[0])

        description = soup.select_one('p.fhJOs1.bs-read-more__text')
        description_text = description.get_text(strip=True) if description else ''

        # Extract additional details
        specifications = {}
        spec_items = soup.select('.specification-item') or soup.select('.product-specs tr')
        for item in spec_items:
            try:
                if item.select('.spec-key') and item.select('.spec-value'):
                    key = item.select_one('.spec-key').get_text(strip=True)
                    value = item.select_one('.spec-value').get_text(strip=True)
                    specifications[key] = value
                elif len(item.find_all('td')) == 2:
                    cells = item.find_all('td')
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    specifications[key] = value
            except:
                continue

        # Extract images
        additional_images = []
        img_elements = soup.select('img[src*="basalam"]') or soup.select('.product-gallery img')
        for img in img_elements:
            src = img.get('src') or img.get('data-src')
            if src and src not in additional_images and 'basalam' in src:
                additional_images.append(src)

        # Extract reviews
        reviews = []
        review_elements = soup.select('.review-item') or soup.select('.comment-item')
        for review in review_elements[:5]:  # Limit to 5 reviews
            try:
                review_text = review.get_text(strip=True)
                if review_text and len(review_text) > 10:
                    reviews.append(review_text)
            except:
                continue

        # Extract rating info
        rating_element = soup.select_one('.rating-average') or soup.select_one('[class*="rating"]')
        rating = 0.0
        if rating_element:
            rating_text = rating_element.get_text()
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                rating = float(rating_match.group(1))

        # Extract vendor info
        vendor_element = soup.select_one('.vendor-name') or soup.select_one('[class*="seller"]')
        vendor_name = vendor_element.get_text(strip=True) if vendor_element else ''

        return {
            'url': url,
            'name': name_text,
            'price': price_numeric,
            'price_text': price_text,
            'description': description_text,
            'specifications': specifications,
            'additional_images': additional_images,
            'reviews': reviews,
            'rating': rating,
            'vendor_name': vendor_name,
            'crawled_successfully': True
        }
        
    except requests.RequestException as e:
        return {
            'error': f'خطا در دریافت صفحه: {str(e)}',
            'url': url,
            'crawled_successfully': False
        }
    except Exception as e:
        return {
            'error': f'خطا در پردازش صفحه: {str(e)}',
            'url': url,
            'crawled_successfully': False
        }

@tool
def batch_crawl_products(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Crawl multiple product pages in batch.
    
    Args:
        urls: List of product URLs to crawl
        
    Returns:
        List of crawled product data
    """
    results = []
    for url in urls[:10]:  # Limit to 10 products to avoid overloading
        try:
            result = crawl_product_page(url)
            results.append(result)
        except Exception as e:
            results.append({
                'url': url,
                'error': str(e),
                'crawled_successfully': False
            })
    
    return results

if __name__ == "__main__":
    test_url = "https://basalam.com/p/16078271"
    import json
    result = crawl_product_page(test_url)
    print(json.dumps(result, ensure_ascii=False, indent=2))
