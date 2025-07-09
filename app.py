
import streamlit as st
import re
from chat import get_agent_response, get_recent_products

st.set_page_config(page_title="دستیار خرید هوشمند", layout="wide")

st.markdown("""
    <style>
    body {
        direction: rtl;
        font-family: 'Vazir', 'Arial', sans-serif;
    }
    .stTextInput > div > div > input {
        direction: rtl;
        text-align: right;
    }
    .stMarkdown {
        text-align: right;
    }
    .product-image {
        max-width: 100px;
        max-height: 100px;
        object-fit: contain;
        margin: 0 auto;
        display: block;
    }
    .stExpander {
        direction: rtl;
    }
    .stExpander .stMarkdown {
        margin-bottom: 10px;
    }
    .stored-product {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .product-id {
        font-family: monospace;
        background-color: #e1e5fe;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for product management
with st.sidebar:
    st.title("🗂️ مدیریت محصولات")
    
    if st.button("📋 محصولات اخیر"):
        try:
            recent_products = get_recent_products(5)
            if recent_products and not isinstance(recent_products, list) or (isinstance(recent_products, list) and recent_products and 'error' not in recent_products[0]):
                st.success("محصولات اخیر:")
                for product in recent_products[:5]:
                    if isinstance(product, dict) and 'error' not in product:
                        with st.expander(f"📦 {product.get('name', 'نامشخص')[:30]}..."):
                            st.write(f"**قیمت:** {product.get('price', 0):,} تومان")
                            st.write(f"**فروشنده:** {product.get('vendor_name', 'نامشخص')}")
                            st.markdown(f'<div class="product-id">شناسه: {product.get("id", "نامشخص")}</div>', unsafe_allow_html=True)
                            if st.button(f"مشاهده جزئیات", key=f"details_{product.get('id')}"):
                                st.session_state.show_product_details = product.get('id')
            else:
                st.info("هیچ محصولی ذخیره نشده است")
        except Exception as e:
            st.error(f"خطا در دریافت محصولات: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("""
    **راهنمای استفاده:**
    
    🔍 **جستجو:** مثل "کفش زیر 500 هزار"
    
    📦 **جزئیات محصول:** 
    "جزئیات محصول شناسه: [ID]"
    
    📊 **مقایسه محصولات:**
    "مقایسه شناسه: [ID1] با شناسه: [ID2]"
    
    💾 **محصولات ذخیره شده:**
    "محصولات ذخیره شده من"
    """)

st.title("🛒 دستیار خرید هوشمند")
st.markdown("سلام! من دستیار خرید شما هستم. محصولات پیدا شده را ذخیره می‌کنم تا بتوانید بعداً جزئیاتشان را مشاهده کنید!")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_product_details" in st.session_state:
    # Show product details if requested from sidebar
    st.info(f"درحال نمایش جزئیات محصول با شناسه: {st.session_state.show_product_details}")
    user_input = f"جزئیات محصول شناسه: {st.session_state.show_product_details}"
    del st.session_state.show_product_details
    
    try:
        with st.spinner("دریافت جزئیات محصول..."):
            response = get_agent_response(user_input)
        st.markdown(response)
    except Exception as e:
        st.error(f"خطا در دریافت جزئیات: {str(e)}")

def is_valid_image_url(url):
    if not url:
        return False
    return bool(re.match(r".*\.(jpg|jpeg|png|gif|bmp)$", url, re.IGNORECASE))

# Display chat history
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"**شما**: {message['content']}")
        else:
            st.markdown(f"**دستیار**: {message['content']}")
            
            # Enhanced product display
            if "نام کالا" in message["content"]:
                products = re.split(r"[-—]+", message["content"])
                for product in products[1:]:
                    lines = [line.strip() for line in product.strip().split("\n") if line.strip()]
                    product_data = {}
                    for line in lines:
                        if line.startswith("نام کالا:"):
                            product_data["name"] = line.replace("نام کالا:", "").strip()
                        elif line.startswith("قیمت:"):
                            product_data["price"] = line.replace("قیمت:", "").strip()
                        elif line.startswith("شهر فروشنده:"):
                            product_data["city"] = line.replace("شهر فروشنده:", "").strip()
                        elif line.startswith("لینک:"):
                            product_data["link"] = line.replace("لینک:", "").strip()
                        elif line.startswith("تصویر:"):
                            product_data["image"] = line.replace("تصویر:", "").strip()

                    if all(key in product_data for key in ["name", "price", "city", "link"]):
                        with st.expander(f"{product_data['name']} - {product_data['price']}"):
                            col1, col2 = st.columns([1, 2])
                            image_url = product_data.get("image")
                            if image_url and is_valid_image_url(image_url):
                                with col1:
                                    try:
                                        st.markdown(f'<img src="{image_url}" class="product-image">', unsafe_allow_html=True)
                                    except Exception as e:
                                        st.write("ناتوانی در بارگذاری تصویر.")
                            with col2:
                                st.markdown(f"**قیمت**: {product_data['price']}")
                                st.markdown(f"**شهر**: {product_data['city']}")
                                st.markdown(f"[مشاهده محصول]({product_data['link']})")
            
            # Show stored product IDs prominently
            if "💾 محصولات ذخیره شدند!" in message["content"]:
                st.success("✅ محصولات با موفقیت ذخیره شدند!")
                # Extract and highlight product IDs
                product_ids = re.findall(r'[a-f0-9-]{36}', message["content"])
                if product_ids:
                    st.info(f"🔑 تعداد {len(product_ids)} محصول ذخیره شد. از شناسه‌ها برای دسترسی سریع استفاده کنید.")
        
        st.markdown("---")

# Enhanced input area
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.chat_input("چه محصولی می‌خواهید؟ (مثال: «کیف زیر ۳۰۰ هزار تومان»)")

with col2:
    if st.button("🔍 جستجوی پیشرفته"):
        st.session_state.show_advanced_search = True

# Advanced search options
if st.session_state.get("show_advanced_search", False):
    with st.expander("🔧 جستجوی پیشرفته", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("نام محصول:", placeholder="مثال: کفش")
            max_price = st.number_input("حداکثر قیمت (تومان):", min_value=0, step=10000)
        
        with col2:
            min_rating = st.slider("حداقل امتیاز:", 0.0, 5.0, 0.0, 0.5)
            vendor_city = st.text_input("شهر فروشنده:", placeholder="مثال: تهران")
        
        with col3:
            if st.button("🔍 جستجو"):
                query_parts = []
                if search_term:
                    query_parts.append(search_term)
                if max_price > 0:
                    query_parts.append(f"زیر {max_price:,} تومان")
                if min_rating > 0:
                    query_parts.append(f"امتیاز بالای {min_rating}")
                if vendor_city:
                    query_parts.append(f"از {vendor_city}")
                
                if query_parts:
                    user_input = " ".join(query_parts)
                    st.session_state.show_advanced_search = False

submit_button = bool(user_input)

if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.spinner("دستیار در حال جستجو و ذخیره محصولات..."):
            response = get_agent_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"خطا در دریافت پاسخ: {str(e)}")
        st.session_state.messages.append({"role": "assistant", "content": "متأسفم، مشکلی پیش آمد. لطفاً دوباره امتحان کنید."})

    st.rerun()

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ پاک کردن تاریخچه"):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("📋 محصولات ذخیره شده"):
        user_input = "محصولات اخیر من را نشان بده"
        st.session_state.messages.append({"role": "user", "content": user_input})
        try:
            response = get_agent_response(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        except Exception as e:
            st.error(f"خطا: {str(e)}")

with col3:
    if st.button("💡 راهنما"):
        help_text = """
        **نحوه استفاده از دستیار:**
        
        1. **جستجوی ساده:** "کفش مردانه"
        2. **جستجو با قیمت:** "کیف زیر 500 هزار تومان"  
        3. **جستجو با فیلتر:** "عطر از تهران امتیاز بالای 4"
        4. **مشاهده جزئیات:** "جزئیات محصول شناسه: [ID]"
        5. **مقایسه محصولات:** "مقایسه شناسه: [ID1] با شناسه: [ID2]"
        
        **💾 همه محصولات به صورت خودکار ذخیره می‌شوند!**
        """
        st.info(help_text)
