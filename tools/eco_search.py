
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.pydantic_v1 import BaseModel

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("AVALAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AVALAI_API_BASE")

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

class EcoSearchInput(BaseModel):
    query: str

class EcoSearchOutput(BaseModel):
    original_query: str
    expanded_components: List[str]
    search_strategy: str

@tool("concept_components_expand", return_direct=False, args_schema=EcoSearchInput)
def concept_components_expand(query: str) -> EcoSearchOutput:
    """
    شناسایی و استخراج اجزاء و لوازم مرتبط با یک مفهوم کلی.
    این ابزار به طور هوشمند تمام قطعات و لوازم جانبی مرتبط با یک مفهوم را پیدا می‌کند.
    """
    prompt = f"""
    کاربر جستجوی زیر را وارد کرده است: "{query}"

    وظیفه شما این است که:
    1. مفهوم اصلی جستجو را درک کنید
    2. تمام اجزاء، قطعات، لوازم جانبی و موارد مرتبط با این مفهوم را شناسایی کنید
    3. لیستی از کلمات کلیدی جستجو تولید کنید که شامل این اجزاء باشد

    مثال‌ها:
    - اگر جستجو "V60 material" باشد، اجزاء شامل: فیلتر، دریپر، سرور، کتری، قهوه، دانه قهوه، آسیاب قهوه، ترازو، تایمر
    - اگر جستجو "آشپزخانه" باشد، اجزاء شامل: قابلمه، ماهیتابه، کتری، چاقو، تخته برش، ادویه، ظروف
    - اگر جستجو "دوربین عکاسی" باشد، اجزاء شامل: لنز، فلاش، حافظه، باتری، کیف، سه پایه، فیلتر

    قوانین مهم:
    - فقط اجزاء و قطعات واقعی و مرتبط را لیست کنید
    - از کلمات کلیدی فارسی استفاده کنید
    - هر جزء را در یک خط جداگانه بنویسید
    - حداکثر 10 جزء پیشنهاد دهید
    - اجزاء را از مهم‌ترین به کم‌اهمیت‌ترین مرتب کنید

    فرمت پاسخ:
    اجزاء مرتبط:
    - [جزء 1]
    - [جزء 2]
    - [جزء 3]
    ...

    استراتژی جستجو: [توضیح کوتاه درباره نحوه گسترش جستجو]
    """
    
    response = llm.invoke(prompt)
    content = response.content.strip()
    
    # Parse the response to extract components
    components = []
    strategy = ""
    
    lines = content.split('\n')
    in_components = False
    in_strategy = False
    
    for line in lines:
        line = line.strip()
        if 'اجزاء مرتبط:' in line:
            in_components = True
            continue
        elif 'استراتژی جستجو:' in line:
            in_components = False
            in_strategy = True
            strategy = line.replace('استراتژی جستجو:', '').strip()
            continue
        elif in_strategy:
            strategy += " " + line
        elif in_components and line.startswith('-'):
            component = line.replace('-', '').strip()
            if component:
                components.append(component)
    
    return EcoSearchOutput(
        original_query=query,
        expanded_components=components[:10],  # Limit to 10 components
        search_strategy=strategy or "جستجوی گسترده برای یافتن تمام اجزاء مرتبط"
    )

if __name__ == "__main__":
    # Test the tool
    test_query = "V60 material"
    result = concept_components_expand.invoke({"query": test_query})
    print(f"جستجوی اصلی: {result.original_query}")
    print(f"اجزاء گسترده شده:")
    for component in result.expanded_components:
        print(f"  - {component}")
    print(f"استراتژی: {result.search_strategy}")
