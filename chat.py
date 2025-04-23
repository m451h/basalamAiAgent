
import os
from operator import itemgetter
from dotenv import load_dotenv
from basalam_search import search_basalam

from langchain.chat_models import init_chat_model
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain import hub


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE")


with open("prompts/base.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()


llm = init_chat_model("llama-3.3-70b-versatile", model_provider="openai")
llm_with_tools = llm.bind_tools([search_basalam])

prompt = hub.pull("hwchase17/openai-tools-agent")
prompt.messages[0].prompt.template = system_prompt

tools = [search_basalam]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


def get_agent_response(user_input: str) -> str:
    result = agent_executor.invoke({"input": user_input})
    return result["output"]
