import os
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel
from typing import Literal
from langchain.chat_models import init_chat_model

# Load env
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("AVALAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AVALAI_API_BASE")


llm = init_chat_model("gpt-4o-mini", model_provider="openai")
# 🔹 تعریف ورودی ابزار
class IntentInput(BaseModel):
    input: str

# 🔹 تعریف خروجی ابزار
class IntentOutput(BaseModel):
    intent: Literal["search_product", "contact_seller", "other"]


# 🔹 ابزار تشخیص نیت
@tool("detect_intent", return_direct=False, args_schema=IntentInput)
def detect_intent(input: str) -> IntentOutput:
    """
    تشخیص نیت کاربر از پیامش.
    """
    prompt = f"""
    پیام زیر از کاربر دریافت شده:
    "{input}"
    
    با توجه به پیام، نیت کاربر رو به صورت یکی از این سه حالت مشخص کن:
    - search_product
    - contact_seller
    - other
    
    فقط مقدار یکی از اون‌ها رو به صورت `intent: <value>` چاپ کن.
    """
    result = llm.invoke(prompt)

    content = result.content.strip().lower()
    if "search_product" in content:
        return IntentOutput(intent="search_product")
    elif "contact_seller" in content:
        return IntentOutput(intent="contact_seller")
    else:
        return IntentOutput(intent="other")


# ✅ برای تست مستقیم:
if __name__ == "__main__":
    user_input = "برو از فروشنده بپرس کی می‌فرسته"
    result = detect_intent.invoke({"input": user_input})
    print(result)
