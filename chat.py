
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

# Check if API key exists before setting it
avalai_api_key = os.getenv("AVALAI_API_KEY")
avalai_api_base = os.getenv("AVALAI_API_BASE")

if avalai_api_key:
    os.environ["OPENAI_API_KEY"] = avalai_api_key
else:
    raise ValueError("AVALAI_API_KEY environment variable is not set. Please add it to your .env file.")

if avalai_api_base:
    os.environ["OPENAI_API_BASE"] = avalai_api_base

with open("prompts/base.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Initialize the LLM properly
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE")
)

# Enhanced tools list with product management
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

# Create a proper prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history", optional=True),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

chat_history = []
stored_products = {}  # Keep track of products by internal ID

def process_and_store_products(products: list, search_query: str = "") -> dict:
    """
    Process search results, crawl detailed info, and store products.
    Returns a mapping of product IDs to internal storage IDs.
    """
    stored_mapping = {}
    
    for product in products[:5]:  # Limit to 5 products to avoid overwhelming
        try:
            # Get the full URL
            short_url = product.get("link", "")
            vendor_name = product.get("vendor_name", "")
            
            if short_url and vendor_name:
                full_url = fix_basalam_product_url(short_url, vendor_name)
                
                # Crawl detailed information
                detailed_info = crawl_product_page(full_url)
                
                if detailed_info.get('crawled_successfully', False):
                    # Merge basic info with detailed info
                    enhanced_product = {
                        **product,
                        **detailed_info,
                        'basalam_id': product.get('product_id'),
                        'search_query': search_query
                    }
                    
                    # Save to database
                    internal_id = save_product_details(enhanced_product, search_query)
                    
                    if "شناسه:" in internal_id:
                        # Extract the actual ID from the response
                        actual_id = internal_id.split("شناسه: ")[1].strip()
                        stored_mapping[product.get('product_id', '')] = actual_id
                        stored_products[actual_id] = enhanced_product
                        
                        print(f"✅ محصول ذخیره شد: {product.get('name', 'نامشخص')} (ID: {actual_id})")
        
        except Exception as e:
            print(f"❌ خطا در پردازش محصول: {str(e)}")
            continue
    
    return stored_mapping

def get_agent_response(user_input: str) -> str:
    global chat_history, stored_products
    
    try:
        # Check if user is asking about stored products
        if any(keyword in user_input.lower() for keyword in ['ذخیره', 'محصولات قبلی', 'جزئیات محصول', 'مقایسه']):
            # Handle stored product queries directly
            if 'جزئیات محصول' in user_input and 'شناسه' in user_input:
                # Extract ID from user input
                import re
                id_match = re.search(r'شناسه[:\s]*([a-f0-9-]+)', user_input)
                if id_match:
                    product_id = id_match.group(1)
                    product_details = get_product_details(product_id)
                    if product_details and 'error' not in product_details:
                        return format_detailed_product(product_details)
            
            elif 'مقایسه' in user_input:
                # Extract multiple IDs for comparison
                import re
                ids = re.findall(r'[a-f0-9-]{36}', user_input)
                if len(ids) >= 2:
                    comparison = compare_products(ids[:3])  # Max 3 products
                    return format_product_comparison(comparison)

        # For search queries, directly call the search function
        if any(keyword in user_input.lower() for keyword in ['جستجو', 'پیدا', 'کالا', 'محصول', 'خرید']):
            try:
                # Direct search approach
                products = search_basalam(user_input)
                
                if products:
                    # Format the response
                    response = f"🛍️ **نتایج جستجو برای '{user_input}':**\n\n"
                    
                    for i, product in enumerate(products[:10], 1):
                        response += f"**{i}. {product.get('name', 'نامشخص')}**\n"
                        response += f"• قیمت: {product.get('price', 0):,} تومان\n"
                        response += f"• فروشنده: {product.get('vendor_name', 'نامشخص')}\n"
                        response += f"• شهر: {product.get('vendor_city', 'نامشخص')}\n"
                        if product.get('rating'):
                            response += f"• امتیاز: {product.get('rating', 0)}/5\n"
                        response += f"• [مشاهده محصول]({product.get('link', '')})\n\n"
                    
                    # Process and store products
                    print(f"🔄 پردازش و ذخیره {len(products)} محصول...")
                    stored_mapping = process_and_store_products(products, user_input)
                    
                    if stored_mapping:
                        response += "\n💾 **محصولات ذخیره شدند!** برای مشاهده جزئیات بیشتر از این شناسه‌ها استفاده کنید:\n"
                        for basalam_id, internal_id in stored_mapping.items():
                            product_name = stored_products.get(internal_id, {}).get('name', 'نامشخص')
                            response += f"• {product_name[:40]}...: `{internal_id}`\n"
                        
                        response += f"\n**مثال:** «جزئیات محصول شناسه: {list(stored_mapping.values())[0]}»"
                    
                    return response
                else:
                    return "❌ متأسفانه محصولی با این مشخصات پیدا نشد. لطفاً عبارت جستجو را تغییر دهید."
                    
            except Exception as e:
                print(f"❌ خطا در جستجو: {str(e)}")
                return f"❌ خطا در جستجو: {str(e)}"
        
        # Use agent for other queries
        result = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": result["output"]})
        
        return result["output"]
        
    except Exception as e:
        print(f"❌ خطا در پردازش درخواست: {str(e)}")
        return f"❌ متأسفم، مشکلی پیش آمد: {str(e)}"

def format_detailed_product(product: dict) -> str:
    """Format detailed product information for display"""
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
    test_input = "کیف زیر ۵۰۰ هزار تومان"
    response = get_agent_response(test_input)
    print("Agent response:", response)
