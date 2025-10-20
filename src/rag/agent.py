from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import create_retriever_tool
from langchain.agents import AgentExecutor, create_tool_calling_agent


class RAGAgent:
    """Агент, использующий retriever для ответов на вопросы по внутренней документации."""

    def __init__(
        self, vector_store, llm: BaseChatModel, number_of_retrieved_documents: int = 5
    ):
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": number_of_retrieved_documents,
                "fetch_k": number_of_retrieved_documents * 4,
            },
        )
        self.llm = llm

        self._agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """Определяет промпт, загружает инструмент и создает агента"""

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Ты - технический ассистент компании Positive Technologies.
                    Отвечай только на основе предоставленного контекста.
                    Если ответа нет в контексте, скажи: "В предоставленной документации нет информации"."""
                ),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        tools = [
            create_retriever_tool(
                retriever=self.retriever,
                name="RAG",
                description="Для поиска информации во внутренней документации",
            ),
        ]

        agent = create_tool_calling_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            handle_parsing_errors=True,
        )
        return agent_executor

    def ask(self, query: str) -> dict[str, Any]:
        """Выдает ответ на запрос пользователя, используя AgentExecutor"""
        response = self._agent_executor.invoke({"input": query})
        print(f"\n\nresponse:{response}\n\n")
        if isinstance(response, dict):
            return response.get("output", "Не удалось получить ответ.")
        return str(response)
