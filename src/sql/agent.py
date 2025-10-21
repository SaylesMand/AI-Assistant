from pathlib import Path

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.agents import create_agent


class SQLAgent:
    """Агент, использующий SQL-запросы для ответов на вопросы по базе данных."""

    def __init__(self, db_path: str, llm: BaseChatModel):
        self.db_path = db_path
        self.llm = llm
        self.db = self._load_database()

        # Создаём toolkit и инструменты
        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.tools = toolkit.get_tools()

        self.prompt = """Ты - технический ассистент, специализирующийся на SQL.
                    Твоя задача - анализировать вопрос пользователя и формировать корректные SQL-запросы.
                    Используй только предоставленные инструменты и данные из базы.

                    Правила:
                    - Если SQL-запрос успешно выполнился и вернул данные, покажи их пользователю.
                    - Если запрос вернул пустой результат, ответь: "В предоставленной базе данных нет информации."
                    - Не выдумывай ответов. Не добавляй посторонние комментарии.
                    - Если результат неоднозначен, уточни у пользователя.
                    """

        self.agent = create_agent(self.llm, self.tools, system_prompt=self.prompt)

    def _load_database(self) -> SQLDatabase:
        """Инициализирует LangChain SQLDatabase, используя локальную SQLite БД."""
        db_file = Path(self.db_path).resolve()
        if not db_file.exists():
            raise FileNotFoundError(
                f"SQL база данных {db_file} не найдена. "
                "Проверь путь или загрузите .db файл."
            )
        return SQLDatabase.from_uri(f"sqlite:///{db_file}")

    def ask(self, query: str) -> str:
        """Обрабатывает запрос пользователя и возвращает ответ от SQL агента."""
        response = self.agent.invoke({"messages": [{"role": "user", "content": query}]})

        return response["messages"][-1].content