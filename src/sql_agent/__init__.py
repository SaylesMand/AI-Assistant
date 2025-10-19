from src.config import settings
from src.utils.models.llm_factory import create_chat_model
from .agent import SQLAgent


def load_sql_agent():
    llm = create_chat_model()
    agent = SQLAgent(db_path=settings.DB_PATH, llm=llm)
    return agent

# query = "Какая роль у сотрудника Jane Doe?"
