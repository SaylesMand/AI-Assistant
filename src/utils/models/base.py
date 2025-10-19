from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings


class BaseLLMProvider(ABC):
    """Базовый интерфейс для всех LLM-провайдеров"""

    @abstractmethod
    def create_chat(self) -> BaseChatModel:
        """Создает чат-модель"""
        pass

    @abstractmethod
    def create_embedding(self) -> Embeddings:
        """Создает эмбеддинг модель"""
        pass
