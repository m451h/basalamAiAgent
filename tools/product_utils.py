import re
from langchain_core.tools import tool

@tool
def fix_basalam_product_url(short_url: str, vendor_name: str) -> str:
    """
    Converts a short Basalam product URL (https://basalam.com/p/12345678)
    to a full product URL (https://basalam.com/{vendor_name}/product/{id})
    """
    match = re.match(r"https://basalam.com/p/(\d+)", short_url)
    if match and vendor_name:
        product_id = match.group(1)
        return f"https://basalam.com/{vendor_name}/product/{product_id}"
    return short_url

# Example usage:
if __name__ == "__main__":
    short = "https://basalam.com/p/10318087"
    vendor = "pejmanshoes"
    print(fix_basalam_product_url(short, vendor))
