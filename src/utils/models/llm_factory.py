from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from src.config import settings
from .base import BaseLLMProvider

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

_PROVIDERS: dict[str, BaseLLMProvider] = {}


def register_provider(name: str):
    """Регистрирует провайдера в глобальном реестре"""

    def decorator(cls: BaseLLMProvider):
        _PROVIDERS[name.lower()] = cls
        return cls

    return decorator


@register_provider("mistral")
class MistralProvider(BaseLLMProvider):
    def create_chat(self) -> BaseChatModel:
        return ChatMistralAI(model=settings.LLM_MODEL, api_key=settings.API_KEY)

    def create_embedding(self) -> Embeddings:
        return MistralAIEmbeddings(
            model=settings.EMBEDDING_MODEL, api_key=settings.API_KEY
        )


@register_provider("openai")
class OpenAIProvider(BaseLLMProvider):
    def create_chat(self) -> BaseChatModel:
        return ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.API_KEY)

    def create_embedding(self) -> Embeddings:
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL, api_key=settings.API_KEY
        )


@register_provider("ollama")
class OllamaProvider(BaseLLMProvider):
    def create_chat(self) -> BaseChatModel:
        return ChatOllama(
            model=settings.LLM_MODEL,
            validate_model_on_init=True,
            temperature=0.8,
        )

    def create_embedding(self) -> Embeddings:
        return OllamaEmbeddings(model=settings.EMBEDDING_MODEL)


@register_provider("vllm")
class VLLMProvider(BaseLLMProvider):
    """vLLM использует OpenAI-совместимый API"""

    def create_chat(self) -> BaseChatModel:
        return ChatOpenAI(model=settings.LLM_MODEL)

    def create_embedding(self) -> Embeddings:
        return OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)


def get_provider() -> BaseLLMProvider:
    """Возвращает экземпляр LLM-провайдера по settings.LLM_MODE"""
    mode = settings.LLM_MODE.lower()
    provider_cls = _PROVIDERS.get(mode)
    if not provider_cls:
        raise ValueError(
            f"Неизвестный LLM_MODE: {mode}. Зарегистрированные: {list(_PROVIDERS.keys())}"
        )
    return provider_cls()


def create_chat_model() -> BaseChatModel:
    """Создает LLM в зависимости от выбранного провайдера"""
    return get_provider().create_chat()


def create_embedding_model() -> Embeddings:
    """Создает эмбеддинг модель в зависимости от выбранного провайдера"""
    return get_provider().create_embedding()
