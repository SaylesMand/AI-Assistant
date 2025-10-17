from langchain_core.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class RAGPipeline:
    """Объединяет retrieval + генерацию ответа."""

    def __init__(self, vector_store, api_key: str, top_k: int = 3):
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
        self.llm = ChatMistralAI(model="mistral-small-latest", api_key=api_key)
        self.prompt = PromptTemplate.from_template(
            """
            Ты — технический ассистент компании Positive Technologies.
            Используй только предоставленный контекст, не выдумывай.
            Если ответа нет в контексте, скажи "В предоставленной документации нет информации".

            Контекст:
            {context}

            Вопрос: {question}

            Ответ:
            """
        )

    def _format_docs(self, docs):
        return "\n\n".join(d.page_content for d in docs)

    def ask(self, question: str) -> str:
        chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return chain.invoke(question)
