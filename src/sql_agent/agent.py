from typing import Any
from pathlib import Path

from langchain_mistralai import ChatMistralAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent

from src.config import settings


class SQLAgent:
    def __init__(self, db_path: str, llm: ChatMistralAI):
        self.db_path = db_path
        self.llm = llm
        self._agent_executor = self._create_agent()

    def _load_database(self) -> SQLDatabase:
        """Инициализирует LangChain SQLDatabase, используя локальную БД"""
        db_file = Path(self.db_path).resolve()
        if not db_file.exists():
            raise FileNotFoundError(
                f"SQL database {db_file} не найден."
                "Пожалуйста, загрузите .db файл в начале."
            )
        return SQLDatabase.from_uri(f"sqlite:///{db_file}")

    def _create_agent(self) -> AgentExecutor:
        """Загружает SQL toolkit, определяет промпт и создает агента"""
        db = self._load_database()
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        tools = toolkit.get_tools()
            
        # Создаем промпт для инструментов
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful SQL expert. Use the tools to query the database."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Создаем агента с поддержкой инструментов
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
        return agent_executor

    def get_response(self, query: str) -> dict[str, Any]:
        """Выдает ответ на запрос пользователя, используя AgentExecutor"""
        response = self._agent_executor.invoke({"input": query})
        return response.get("output", "Не удалось получить ответ.")
    
if __name__ == "__main__":    
    llm = ChatMistralAI(model_name="mistral-small-latest", api_key=settings.MISTRAL_API_KEY)
    agent = SQLAgent(db_path=settings.DB_PATH, llm=llm)

    query = "What is the role of Jane Doe's employee?"
    print(agent.get_response(query=query))