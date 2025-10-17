import json
from langchain_core.documents import Document


class DocumentLoader:
    """Чтение и представление документов"""
    def __init__(self, path: str):
        self.path = path

    def load(self) -> list[Document]:
        """Загружает данные из JSON и возвращает список Document."""
        with open("D:/Programming/pet-projects/AI-Assistant/data_copy2.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        documents = []
        for url, doc_data in data.items():
            metadata = {"url": url, "title": doc_data.get("title", "Без заголовка")}
            content = doc_data.get("content", "")
            documents.append(Document(page_content=content, metadata=metadata))
        return documents
        

        


