from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent

from src.agent_router.tools.rag_tool import RAGTool
from src.agent_router.tools.sql_tool import SQLTool
from src.agent_router.tools.web_tool import WebTool

from langchain_core.tools import Tool


class RouterAgent:
    """Роутер, который решает, какой инструмент использовать."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.tools = {"rag": RAGTool(), "sql": SQLTool(), "web": WebTool()}
        self.memory = ConversationBufferMemory(
            return_messages=True, memory_key="chat_history"
        )

        self._agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """определяет промпт, создает заданные инструменты и агента"""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    Ты - интеллектуальный ассистент компании Positive Technologies. 
                    Ты можешь использовать три инструмента, чтобы найти нужную информацию:

                    1. **RAG** - используй для поиска данных во внутренней документации компании.  
                    2. **SQL** - используй для поиска информации в базе данных (структурированные данные, таблицы, сотрудники, роли, специализации и т.д.).  
                    3. **Web** - используй для поиска в интернете (новости, общие сведения, внешние источники).

                    Твоя задача - ответить на вопрос пользователя максимально точно и кратко, **используя только достоверные источники**.  
                    Действуй по следующему плану:

                    1. Проанализируй запрос и определи, какой инструмент наиболее уместен.  
                    2. Используй этот инструмент для получения ответа.  
                    3. Если инструмент не дал ответа (например, вернул "нет информации", "пусто", "не найдено" и т.п.),  
                    пробуй другой инструмент.  
                    4. При необходимости можешь **комбинировать результаты** нескольких инструментов (например, SQL + RAG, RAG + Web, SQL + Web или SQL + RAG + Web).  
                    5. Если после использования всех инструментов информации нет, ответь строго:  
                    **"Не удалось найти ответ."**

                    Никогда не выдумывай ответы.  
                    Отвечай только на основе найденных данных.

                    Даже если ты уверен в ответе, **всегда проверяй себя с помощью подходящего инструмента**.
                    Никогда не полагайся только на память. 
                    Если есть сомнение, вызови RAG, SQL или Web для уточнения.
                    """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
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
            Tool(
                name="Web",
                func=self.tools["web"].run,
                description="Для поиска информации в интернете",
            ),
        ]
        agent = create_tool_calling_agent(self.llm, tools=tools, prompt=prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.memory,
        )
        return agent_executor

    def ask(self, query: str) -> str:
        """Выдает ответ на запрос пользователя, используя AgentExecutor"""
        response = self._agent_executor.invoke({"input": query})
        if isinstance(response, dict):
            return response.get("output", "Не удалось получить ответ.")
        return str(response)
