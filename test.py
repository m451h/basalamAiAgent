import os
from operator import itemgetter
from basalam_search import search_basalam

from langchain.chat_models import init_chat_model
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain import hub

from dotenv import load_dotenv

# بارگذاری .env
load_dotenv()

# ست کردن API config از .env
os.environ["OPENAI_API_KEY"] = os.getenv("AVALAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AVALAI_API_BASE")


# بارگذاری پرامپت
with open("prompts/base.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# مدل LLM و ابزار جستجو
llm = init_chat_model("gpt-4o-mini", model_provider="openai")
llm_with_tools = llm.bind_tools([search_basalam])

# ساخت عامل هوشمند
prompt = hub.pull("hwchase17/openai-tools-agent")
prompt.messages[0].prompt.template = system_prompt

tools = [search_basalam]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
'''
# اجرای درخواست کاربر
#user_input = "عسل طبیعی با قیمت مناسب و کیفیت بالا"
user_input = input("لطفاً عبارت جستجو را وارد کنید: ")
response = agent_executor.invoke({"input": user_input})

# چاپ خروجی
print("✅ پاسخ دستیار:\n")
print(response["output"])
'''
while True:
    user_input = input("🟢 شما: ")
    if user_input.strip().lower() in ["خروج", "exit", "quit"]:
        break
    response = agent_executor.invoke({"input": user_input})
    print("\n🤖 دستیار:", response["output"])
    print("--------------------------------------------------")