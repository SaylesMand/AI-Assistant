from langchain.agents import create_agent
from langchain_core.tools import Tool
from langgraph.checkpoint.memory import InMemorySaver 
from langchain_core.language_models import BaseChatModel

from src.agent_router.tools.rag_tool import RAGTool
from src.agent_router.tools.sql_tool import SQLTool
from src.agent_router.tools.web_tool import WebTool


class RouterAgent:
    """Агент-оркерстратор"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.tools = {
            "rag": RAGTool(),
            "sql": SQLTool(),
            "web": WebTool(),
        }

        self.prompt = """
                    Ты - интеллектуальный ассистент компании Positive Technologies.
                    У тебя есть три инструмента:
                    1. **RAG** - используй для поиска во внутренней документации компании.
                    2. **SQL** - используй для получения информации из базы данных.
                    3. **Web** - используй для поиска информации в интернете.

                    Правила:
                    - Сначала анализируй вопрос и выбирай инструмент.
                    - Если один инструмент не дал результата, пробуй другой.
                    - Можешь комбинировать инструменты (например, SQL + RAG).
                    - Если ни один инструмент не помог, ответь: "Не удалось найти ответ."
                    - Не выдумывай ответы, опирайся только на достоверные данные.
                    """

        self.tools_list = [
            Tool(
                name="RAG",
                func=self.tools["rag"].run,
                description="Для поиска информации во внутренней документации",
            ),
            Tool(
                name="SQL",
                func=self.tools["sql"].run,
                description="Для получения информации из базы данных",
            ),
            Tool(
                name="Web",
                func=self.tools["web"].run,
                description="Для поиска информации в интернете",
            ),
        ]

        self.agent = create_agent(self.llm, self.tools_list, system_prompt=self.prompt, checkpointer=InMemorySaver())


    def ask(self, query: str) -> str:
        """Отправляет запрос агенту с учётом контекста диалога."""
        response = self.agent.invoke(
            input={"messages": [{"role": "user", "content": query}]},
            config={"configurable": {"thread_id": "1"}},
        )
        return response["messages"][-1].content
