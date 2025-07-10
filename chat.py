
import os
from operator import itemgetter
from dotenv import load_dotenv

from tools.basalam_search import search_basalam
from tools.intent_detector import detect_intent
from tools.generate_message import generate_seller_message
from tools.product_utils import fix_basalam_product_url
from tools.product_crawler import crawl_product_page, batch_crawl_products
from tools.product_manager import (
    save_product_details, 
    get_product_details, 
    search_saved_products, 
    get_recent_products,
    compare_products
)

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

print("🔧 [DEBUG] Starting chat.py initialization...")

# Check if API key exists before setting it
avalai_api_key = os.getenv("AVALAI_API_KEY")
avalai_api_base = os.getenv("AVALAI_API_BASE")

print(f"🔧 [DEBUG] API Key exists: {bool(avalai_api_key)}")
print(f"🔧 [DEBUG] API Base exists: {bool(avalai_api_base)}")

if avalai_api_key:
    os.environ["OPENAI_API_KEY"] = avalai_api_key
else:
    raise ValueError("AVALAI_API_KEY environment variable is not set. Please add it to your .env file.")

if avalai_api_base:
    os.environ["OPENAI_API_BASE"] = avalai_api_base

print("🔧 [DEBUG] Loading system prompt...")
with open("prompts/base.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()
print(f"🔧 [DEBUG] System prompt loaded: {len(system_prompt)} characters")

# Initialize the LLM properly
print("🔧 [DEBUG] Initializing LLM...")
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE")
)
print("🔧 [DEBUG] LLM initialized successfully")

# Enhanced tools list with product management
print("🔧 [DEBUG] Setting up tools...")
tools = [
    search_basalam, 
    detect_intent, 
    generate_seller_message, 
    fix_basalam_product_url, 
    crawl_product_page,
    batch_crawl_products,
    save_product_details,
    get_product_details,
    search_saved_products,
    get_recent_products,
    compare_products
]
print(f"🔧 [DEBUG] Tools setup complete: {len(tools)} tools loaded")

# Create a proper prompt template
print("🔧 [DEBUG] Creating prompt template...")
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history", optional=True),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

print("🔧 [DEBUG] Creating agent...")
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
print("🔧 [DEBUG] Agent created successfully")

chat_history = []
stored_products = {}  # Keep track of products by internal ID

print("🔧 [DEBUG] Chat.py initialization complete!")

def process_and_store_products(products: list, search_query: str = "") -> dict:
    """
    Process search results, crawl detailed info, and store products.
    Returns a mapping of product IDs to internal storage IDs.
    """
    print(f"🔧 [DEBUG] process_and_store_products called with {len(products)} products")
    stored_mapping = {}
    
    for i, product in enumerate(products[:5]):  # Limit to 5 products to avoid overwhelming
        print(f"🔧 [DEBUG] Processing product {i+1}/{min(len(products), 5)}: {product.get('name', 'Unknown')}")
        try:
            # Get the full URL
            short_url = product.get("link", "")
            vendor_name = product.get("vendor_name", "")
            
            print(f"🔧 [DEBUG] Product URL: {short_url}")
            print(f"🔧 [DEBUG] Vendor: {vendor_name}")
            
            if short_url and vendor_name:
                print("🔧 [DEBUG] Fixing product URL...")
                full_url = fix_basalam_product_url(short_url, vendor_name)
                print(f"🔧 [DEBUG] Full URL: {full_url}")
                
                # Crawl detailed information
                print("🔧 [DEBUG] Crawling product page...")
                detailed_info = crawl_product_page(full_url)
                print(f"🔧 [DEBUG] Crawl result: {detailed_info.get('crawled_successfully', False)}")
                
                if detailed_info.get('crawled_successfully', False):
                    # Merge basic info with detailed info
                    enhanced_product = {
                        **product,
                        **detailed_info,
                        'basalam_id': product.get('product_id'),
                        'search_query': search_query
                    }
                    
                    print("🔧 [DEBUG] Saving product to database...")
                    # Save to database
                    internal_id = save_product_details(enhanced_product, search_query)
                    print(f"🔧 [DEBUG] Save result: {internal_id}")
                    
                    if "شناسه:" in internal_id:
                        # Extract the actual ID from the response
                        actual_id = internal_id.split("شناسه: ")[1].strip()
                        stored_mapping[product.get('product_id', '')] = actual_id
                        stored_products[actual_id] = enhanced_product
                        
                        print(f"✅ محصول ذخیره شد: {product.get('name', 'نامشخص')} (ID: {actual_id})")
                else:
                    print(f"❌ [DEBUG] Failed to crawl product: {product.get('name', 'Unknown')}")
            else:
                print(f"❌ [DEBUG] Missing URL or vendor for product: {product.get('name', 'Unknown')}")
        
        except Exception as e:
            print(f"❌ خطا در پردازش محصول: {str(e)}")
            print(f"🔧 [DEBUG] Full error details: {repr(e)}")
            continue
    
    print(f"🔧 [DEBUG] process_and_store_products completed. Stored {len(stored_mapping)} products")
    return stored_mapping

def get_agent_response(user_input: str) -> str:
    global chat_history, stored_products
    
    print(f"\n🔧 [DEBUG] ======= NEW REQUEST =======")
    print(f"🔧 [DEBUG] User input: '{user_input}'")
    print(f"🔧 [DEBUG] Chat history length: {len(chat_history)}")
    print(f"🔧 [DEBUG] Stored products count: {len(stored_products)}")
    
    try:
        # Check if user is asking about stored products
        stored_keywords = ['ذخیره', 'محصولات قبلی', 'جزئیات محصول', 'مقایسه']
        is_stored_query = any(keyword in user_input.lower() for keyword in stored_keywords)
        print(f"🔧 [DEBUG] Is stored product query: {is_stored_query}")
        
        if is_stored_query:
            print("🔧 [DEBUG] Handling stored product query...")
            # Handle stored product queries directly
            if 'جزئیات محصول' in user_input and 'شناسه' in user_input:
                print("🔧 [DEBUG] Extracting product ID from user input...")
                # Extract ID from user input
                import re
                id_match = re.search(r'شناسه[:\s]*([a-f0-9-]+)', user_input)
                if id_match:
                    product_id = id_match.group(1)
                    print(f"🔧 [DEBUG] Found product ID: {product_id}")
                    product_details = get_product_details(product_id)
                    print(f"🔧 [DEBUG] Product details result: {type(product_details)}")
                    if product_details and 'error' not in product_details:
                        return format_detailed_product(product_details)
                else:
                    print("🔧 [DEBUG] No product ID found in input")
            
            elif 'مقایسه' in user_input:
                print("🔧 [DEBUG] Handling product comparison...")
                # Extract multiple IDs for comparison
                import re
                ids = re.findall(r'[a-f0-9-]{36}', user_input)
                print(f"🔧 [DEBUG] Found IDs for comparison: {ids}")
                if len(ids) >= 2:
                    comparison = compare_products(ids[:3])  # Max 3 products
                    return format_product_comparison(comparison)

        # For any search-like query, always try to search
        print(f"🔍 [DEBUG] Starting search for: {user_input}")
        
        try:
            # Direct search approach - call the search function directly
            print("🔧 [DEBUG] Importing search function...")
            from tools.basalam_search import search_basalam as search_func
            print("🔧 [DEBUG] Search function imported successfully")
            
            print("🔧 [DEBUG] Calling search function...")
            products = search_func(user_input)
            print(f"🔧 [DEBUG] Search function returned: {type(products)}")
            print(f"🔍 Found {len(products) if isinstance(products, list) else 'unknown'} products")
            
            if isinstance(products, list) and len(products) > 0:
                print(f"🔧 [DEBUG] Processing {len(products)} products...")
                # Format the response
                response = f"🛍️ **نتایج جستجو برای '{user_input}':**\n\n"
                
                for i, product in enumerate(products[:10], 1):
                    print(f"🔧 [DEBUG] Formatting product {i}: {product.get('name', 'Unknown')}")
                    response += f"**{i}. {product.get('name', 'نامشخص')}**\n"
                    response += f"• قیمت: {product.get('price', 0):,} تومان\n"
                    response += f"• فروشنده: {product.get('vendor_name', 'نامشخص')}\n"
                    response += f"• شهر: {product.get('vendor_city', 'نامشخص')}\n"
                    if product.get('rating'):
                        response += f"• امتیاز: {product.get('rating', 0)}/5\n"
                    response += f"• [مشاهده محصول]({product.get('link', '')})\n\n"
                
                # Process and store products
                print(f"🔄 پردازش و ذخیره {len(products)} محصول...")
                print("🔧 [DEBUG] Starting process_and_store_products...")
                stored_mapping = process_and_store_products(products, user_input)
                print(f"🔧 [DEBUG] Stored mapping result: {stored_mapping}")
                
                if stored_mapping:
                    response += "\n💾 **محصولات ذخیره شدند!** برای مشاهده جزئیات بیشتر از این شناسه‌ها استفاده کنید:\n"
                    for basalam_id, internal_id in stored_mapping.items():
                        product_name = stored_products.get(internal_id, {}).get('name', 'نامشخص')
                        response += f"• {product_name[:40]}...: `{internal_id}`\n"
                    
                    response += f"\n**مثال:** «جزئیات محصول شناسه: {list(stored_mapping.values())[0]}»"
                
                print(f"🔧 [DEBUG] Final response length: {len(response)} characters")
                return response
            elif isinstance(products, list) and len(products) == 0:
                print("🔧 [DEBUG] Search returned empty list")
                return "❌ متأسفانه محصولی با این مشخصات پیدا نشد. لطفاً عبارت جستجو را تغییر دهید."
            else:
                print(f"🔧 [DEBUG] Unexpected search result type: {type(products)}")
                return "❌ خطا در دریافت نتایج جستجو."
                
        except Exception as e:
            print(f"❌ خطا در جستجو: {str(e)}")
            print(f"🔧 [DEBUG] Search error details: {repr(e)}")
            import traceback
            print(f"🔧 [DEBUG] Full traceback: {traceback.format_exc()}")
            # Provide a helpful fallback response
            return "❌ متأسفانه در حال حاضر امکان جستجو وجود ندارد. لطفاً:\n" \
                   "• اتصال اینترنت خود را بررسی کنید\n" \
                   "• چند دقیقه بعد دوباره تلاش کنید\n" \
                   "• یا از طریق سایت basalam.com جستجو کنید"
        
    except Exception as e:
        print(f"❌ خطا در پردازش درخواست: {str(e)}")
        print(f"🔧 [DEBUG] Main error details: {repr(e)}")
        import traceback
        print(f"🔧 [DEBUG] Full traceback: {traceback.format_exc()}")
        return f"❌ متأسفم، مشکلی پیش آمد: {str(e)}"

def format_detailed_product(product: dict) -> str:
    """Format detailed product information for display"""
    print(f"🔧 [DEBUG] Formatting detailed product: {product.get('name', 'Unknown')}")
    output = f"📦 **جزئیات کامل محصول**\n\n"
    output += f"**نام:** {product.get('name', 'نامشخص')}\n"
    output += f"**قیمت:** {product.get('price', 0):,} تومان\n"
    output += f"**امتیاز:** {product.get('rating', 0)} از 5\n"
    output += f"**فروشنده:** {product.get('vendor_name', 'نامشخص')}\n"
    output += f"**شهر:** {product.get('vendor_city', 'نامشخص')}\n\n"
    
    if product.get('description'):
        output += f"**توضیحات:**\n{product['description']}\n\n"
    
    if product.get('specifications'):
        output += "**مشخصات:**\n"
        for key, value in product['specifications'].items():
            output += f"• {key}: {value}\n"
        output += "\n"
    
    if product.get('reviews'):
        output += "**نظرات مشتریان:**\n"
        for i, review in enumerate(product['reviews'][:3], 1):
            output += f"{i}. {review[:100]}...\n"
        output += "\n"
    
    output += f"**لینک:** {product.get('link', product.get('url', ''))}\n"
    
    return output

def format_product_comparison(comparison: dict) -> str:
    """Format product comparison for display"""
    print(f"🔧 [DEBUG] Formatting product comparison")
    if 'error' in comparison:
        return f"❌ {comparison['error']}"
    
    products = comparison.get('products', [])
    if len(products) < 2:
        return "❌ حداقل دو محصول برای مقایسه نیاز است"
    
    output = "📊 **مقایسه محصولات**\n\n"
    
    for i, product in enumerate(products, 1):
        output += f"**محصول {i}: {product.get('name', 'نامشخص')}**\n"
        output += f"• قیمت: {product.get('price', 0):,} تومان\n"
        output += f"• امتیاز: {product.get('rating', 0)}\n"
        output += f"• فروشنده: {product.get('vendor_name', 'نامشخص')}\n\n"
    
    comp_data = comparison.get('comparison', {})
    prices = comp_data.get('prices', [])
    
    if prices:
        min_price = min(prices)
        max_price = max(prices)
        output += f"**خلاصه قیمت:**\n"
        output += f"• ارزان‌ترین: {min_price:,} تومان\n"
        output += f"• گران‌ترین: {max_price:,} تومان\n"
        output += f"• اختلاف قیمت: {max_price - min_price:,} تومان\n"
    
    return output

# Simple test
if __name__ == "__main__":
    print("🔧 [DEBUG] Running test...")
    test_input = "کیف زیر ۵۰۰ هزار تومان"
    print(f"🔧 [DEBUG] Test input: {test_input}")
    response = get_agent_response(test_input)
    print("🔧 [DEBUG] Test completed")
    print("Agent response:", response)
