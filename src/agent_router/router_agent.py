from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent

from src.agent_router.tools.rag_tool import RAGTool
from src.agent_router.tools.sql_tool import SQLTool

from langchain_core.tools import Tool


class RouterAgent:
    """Роутер, который решает, какой инструмент использовать."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.tools = {"rag": RAGTool(), "sql": SQLTool()}
        self._agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """определяет промпт, создает заданные инструменты и агента"""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    Ты - технический ассистент. У теб есть два инструмента:
                    - RAG - если вопрос касается внутренней документации Positive Technologies;
                    - SQL - если тебе нужно получить данные из базы данных.
                    Выбери инструмент или используй их комбинацию. Отвечай четко и точно, а главное, не выдумывай.
                    Если ответа нет в документации и базе данных, скажи "В предоставленной документации и БД нет информации."
                    """,
                ),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        tools = [
            Tool(
                name="RAG",
                func=self.tools["rag"].run,
                description="Для поиска информации во внутренней документации",
            ),
            Tool(
                name="SQL",
                func=self.tools["sql"].run,
                description="Для получения информации из SQL базы данных",
            ),
        ]
        agent = create_openai_tools_agent(self.llm, tools=tools, prompt=prompt)
        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )
        return agent_executor

    def ask(self, query: str) -> str:
        """Выдает ответ на запрос пользователя, используя AgentExecutor"""
        response = self._agent_executor.invoke({"input": query})
        return response.get("output", "Не удалось получить ответ.")
