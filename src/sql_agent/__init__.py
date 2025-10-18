from langchain_mistralai import ChatMistralAI

from src.config import settings
from .agent import SQLAgent


def load_sql_agent():
    llm = ChatMistralAI(model_name="mistral-small-latest", api_key=settings.MISTRAL_API_KEY)
    agent = SQLAgent(db_path=settings.DB_PATH, llm=llm)
    return agent

# query = "Какая роль у сотрудника Jane Doe?"
