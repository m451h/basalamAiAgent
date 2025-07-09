import os
from operator import itemgetter
from dotenv import load_dotenv


from langchain.tools import tool
from langchain.chat_models import init_chat_model


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


llm = init_chat_model("gpt-4o-mini", model_provider="openai")

@tool("generate_seller_message", return_direct=False)
def generate_seller_message(product_title: str, question: str) -> str:
    """
    ساخت یک پیام خودمونی، طبیعی و شبیه به انسان برای فروشنده، با استفاده از عنوان محصول و سوال کاربر.
    """
    prompt = f"""
    من می‌خوام یه پیام خیلی طبیعی، خودمونی و مثل حرف زدن آدمای واقعی، برای فروشنده یکی از محصولات سایت باسلام بنویسم.
    
    عنوان محصول: "{product_title}"
    سوال من: "{question}"

    لطفاً فقط خود متن پیام رو برگردون. پیام باید:
    - صمیمی باشه، نه خیلی رسمی
    - مودبانه ولی راحت و بدون اضافه‌گویی
    - لحن انسانی و واقعی داشته باشه، انگار یه آدم واقعی نوشته نه یه ربات

    فقط پیام نهایی رو بده. چیزی دیگه ننویس.
    """
    response = llm.invoke(prompt)
    return response.content.strip()


if __name__ == "__main__":
    test_input = {
        "product_title": "چای سبز ارگانیک نیوشا ۱۰۰ گرمی",
        "question": "چه مدت طول می‌کشه تا این محصول رو ارسال کنید؟"
    }
    result = generate_seller_message.invoke(test_input)
    print("📩 پیام تولید‌شده برای فروشنده:\n", result)