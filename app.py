import streamlit as st
from chat import get_agent_response
import ast  

# Set the page configuration with title and icon
st.set_page_config(page_title="دستیار باسلام", page_icon="🛍️")
st.title("🛒 دستیار هوشمند باسلام")

# CSS for styling the product cards
st.markdown("""
<style>
    .product-card {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
        background-color: #1e1e1e;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .product-image {
        width: 120px;
        height: 120px;
        object-fit: cover;
        border-radius: 10px;
    }
    .product-info {
        color: white;
        font-size: 16px;
        line-height: 1.8;
    }
    .product-info a {
        color: #4FC3F7;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# Text input for the user query
query = st.text_input("چی می‌خوای جستجو کنی؟", placeholder="مثلاً عسل طبیعی یا کفش مردانه زیر ۵۰۰")

if query:
    with st.spinner("در حال جستجو..."):
        response = get_agent_response(query)
    
    try:
        # Attempt to convert the response string to a Python list object
        result_list = ast.literal_eval(response)
        st.success("✅ نتایج پیشنهادی:")

        # Iterate through each product and render as a card
        for i, product in enumerate(result_list, 1):
            name = product.get("name", "نامشخص")
            price_raw = product.get("price", 0)
            price = f"{int(price_raw):,} تومان" if price_raw else "نامشخص"
            image = product.get("image", "")
            link = product.get("link", "#")
            rating = product.get("rating", "نامشخص")
            rating_count = product.get("rating_count", 0)
            vendor_name = product.get("vendor_name", "نامشخص")
            vendor_city = product.get("vendor_city", "نامشخص")

            st.markdown(f"""
            <div class="product-card">
                <img src="{image}" alt="{name}" class="product-image"/>
                <div class="product-info">
                    <b>{i}. {name}</b><br>
                    💰 قیمت: {price}<br>
                    ⭐ امتیاز: {rating} ({rating_count} نظر)<br>
                    🏬 فروشنده: {vendor_name} از {vendor_city}<br>
                    <a href="{link}" target="_blank">🔗 مشاهده در باسلام</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        # Fallback in case the response is not a list of products
        st.success("✅ پاسخ دستیار:")
        st.markdown(response)
