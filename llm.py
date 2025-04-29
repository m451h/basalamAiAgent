import os
from operator import itemgetter
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("AVALAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("AVALAI_API_BASE")

llm = init_chat_model("gpt-4o-mini", model_provider="openai")