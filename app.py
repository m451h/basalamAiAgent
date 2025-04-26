import streamlit as st
import re
from chat import get_agent_response

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
    </style>
""", unsafe_allow_html=True)

st.title("🛒 دستیار خرید هوشمند")
st.markdown("سلام! من دستیار خرید شما هستم. بگویید چه محصولی می‌خواهید، من بهترین گزینه‌ها را برایتان پیدا می‌کنم!")

if "messages" not in st.session_state:
    st.session_state.messages = []

def is_valid_image_url(url):
    if not url:
        return False
    return bool(re.match(r".*\.(jpg|jpeg|png|gif|bmp)$", url, re.IGNORECASE))

for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"**شما**: {message['content']}")
        else:
            st.markdown(f"**دستیار**: {message['content']}")
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
        st.markdown("---")

with st.form(key="user_input_form", clear_on_submit=True):
    user_input = st.text_input("چه محصولی می‌خواهید؟ (مثال: «عسل از قم می‌خوام»)", "")
    submit_button = st.form_submit_button("ارسال")

if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.spinner("دستیار در حال فکر کردن است..."):
            response = get_agent_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"خطا در دریافت پاسخ: {str(e)}")
        st.session_state.messages.append({"role": "assistant", "content": "متأسفم، مشکلی پیش آمد. لطفاً دوباره امتحان کنید."})

    st.rerun()

if st.button("پاک کردن تاریخچه گفتگو"):
    st.session_state.messages = []
    st.rerun()