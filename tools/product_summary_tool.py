import re
from typing import Optional
from tools.product_crawler import crawl_product_page

def summarize_text(text: str, max_sentences: int = 2) -> str:
    """
    Simple extractive summarizer: returns the first N sentences.
    """
    # Split text into sentences (very basic)
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    summary = ' '.join(sentences[:max_sentences])
    return summary

def get_product_summary(product_url: str, max_sentences: int = 2) -> Optional[str]:
    """
    Given a product URL, fetches the product page and returns a summary of its description.
    """
    details = crawl_product_page(product_url)
    if 'description' in details and details['description']:
        return summarize_text(details['description'], max_sentences)
    elif 'error' in details:
        return f"Error fetching product: {details['error']}"
    else:
        return "No description available for this product."

if __name__ == "__main__":
    # Example usage:
    url = "https://basalam.com/p/11116951"  # Replace with a real product URL
    print(get_product_summary(url, max_sentences=2))
