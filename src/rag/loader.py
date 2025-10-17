import json
from pathlib import Path
from langchain_core.documents import Document

from src.config import settings


class DocumentLoader:
    """Чтение и представление документов"""
    def __init__(self, path: str):
        self.path = path

    def _ensure_data_exists(self):
        data_path = Path(settings.DATA_PATH)
        if not data_path.exists():
            raise FileNotFoundError(
                f"Файл {data_path} не найден."
                "\nЗапустите `python -m src.crawler` сначала."
            )
            
    
    def load(self) -> list[Document]:
        """Загружает данные из JSON и возвращает список Document."""
        self._ensure_data_exists()
        with open(settings.DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        documents = []
        for url, doc_data in data.items():
            metadata = {"url": url, "title": doc_data.get("title", "Без заголовка")}
            content = doc_data.get("content", "")
            documents.append(Document(page_content=content, metadata=metadata))
        return documents
        

        


