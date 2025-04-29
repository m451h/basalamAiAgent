import streamlit as st
from tools.intent_detector import detect_intent
from tools.generate_message import generate_seller_message

st.title("🤖 دستیار باسلام")

user_input = st.chat_input("پیام خود را وارد کنید...")

if user_input:
    # مرحله 1: تشخیص نیت
    intent_result = detect_intent.invoke({"input": user_input})

    intent = intent_result["intent"]
    
    st.write(f"🔍 نیت تشخیص داده‌شده: `{intent}`")

    # مرحله 2: اگر قصد پیام دادن به فروشنده بود
    if intent == "contact_seller":
        # برای تست، یک عنوان محصول فرضی وارد می‌کنیم:
        fake_product_title = "عسل طبیعی کوهستان"
        message = generate_seller_message.invoke({
            "product_title": fake_product_title,
            "question": user_input
        })
        print("📩 پیام تولید شده برای فروشنده:")
        print(message)
        st.success("✅ پیام به صورت تست تولید شد (در ترمینال چاپ شد)")

    elif intent == "search_product":
        st.info("🔎 کاربر به دنبال محصول است.")
    else:
        st.warning("❔ نیت قابل تشخیص نیست.")
