from langchain.agents import create_agent
from langchain_core.tools import create_retriever_tool
from langchain_core.language_models.chat_models import BaseChatModel


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

        self.prompt = """Ты - технический ассистент компании Positive Technologies.
                    Отвечай только на основе предоставленного контекста.
                    Если ответа нет в контексте, скажи: "В предоставленной документации нет информации".
                    """
        self.tools = [
            create_retriever_tool(
                retriever=self.retriever,
                name="RAG",
                description="Для поиска информации во внутренней документации",
            ),
        ]
        self.agent = create_agent(self.llm, self.tools, system_prompt=self.prompt)

    def ask(self, query: str) -> str:
        """Обрабатывает запрос пользователя и возвращает ответ от RAG агента."""
        response = self.agent.invoke({"messages": [{"role": "user", "content": query}]})
        # print(f"\n\nreponse:\n{response}\n")
        # response["messages"][-1].pretty_print()
        return response["messages"][-1].content