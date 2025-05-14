import os
from operator import itemgetter
from dotenv import load_dotenv

from tools.basalam_search import search_basalam
from tools.intent_detector import detect_intent
from tools.generate_message import generate_seller_message
from tools.product_utils import fix_basalam_product_url
from tools.product_crawler import crawl_product_page
 

from langchain.chat_models import init_chat_model
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain import hub


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("AVALAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AVALAI_API_BASE")


with open("prompts/base.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()


llm = init_chat_model("gpt-4o-mini", model_provider="openai")

tools = [search_basalam, detect_intent, generate_seller_message]
llm_with_tools = llm.bind_tools(tools)

prompt = hub.pull("hwchase17/openai-tools-agent")
prompt.messages[0].prompt.template = system_prompt

tools = [search_basalam]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


chat_history = []

def get_agent_response(user_input: str) -> str:
    global chat_history
    intent_result = detect_intent.invoke({"input": user_input})
    intent = intent_result.intent

    if intent == "contact_seller":

        product_title = "عنوان محصول نمونه"
        question = user_input  
        message = generate_seller_message.invoke({
            "product_title": product_title,
            "question": question
        })
        print("📩 پیام تولید‌شده برای فروشنده:\n", message)
        return f"پیام برای فروشنده آماده شد ✅ (پیام: {message})"

    else:
        result = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history
        })
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": result["output"]})

        # --- NEW: Try to access products ---

        products = result.get("products", [])
        for product in products:
            short_url = product.get("link")
            vendor = product.get("vendor_name")
            full_url = fix_basalam_product_url(short_url, vendor)
            details = crawl_product_page(full_url)
            print(details)  # Or collect these for further use

        return result["output"]