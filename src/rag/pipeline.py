from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_core.language_models.chat_models import BaseChatModel


class RAGPipeline:
    """Объединяет retrieval + генерацию ответа."""

    def __init__(self, vector_store, llm: BaseChatModel, top_k: int = 3):
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Ты — технический ассистент компании Positive Technologies.
                Используй только предоставленный контекст, не выдумывай.
                Если ответа нет в контексте, скажи: "В предоставленной документации нет информации".""",
                ),
                ("human", "Контекст:\n{context}\n\nВопрос: {question}\n\nОтвет:"),
            ]
        )

    def _format_docs(self, docs):
        return "\n\n".join(d.page_content for d in docs)

    def ask(self, question: str) -> str:
        chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return chain.invoke(question)
