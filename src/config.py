import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API key
    API_KEY = os.getenv("API_KEY")

    # Qdrant
    QDRANT_PATH = os.getenv("QDRANT_PATH", "data/qdrant")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "qdrant_rag")

    # LLM config
    LLM_MODE = os.getenv("LLM_MODE", "mistral")  # ["mistral", "openai", "ollama", "vllm"]
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral-small-latest")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "mistral-embed")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:11434") # for Ollama: http://localhost:11434 or vLLM: http://localhost:8000/v1

    # RAG config
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    TOP_K = int(os.getenv("TOP_K", "3"))

    # Data / DB
    DATA_PATH = os.getenv("DATA_PATH")
    DOCS_URL = os.getenv("DOCS_URL")
    MAX_DEPTH = int(os.getenv("MAX_DEPTH", "1"))
    MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "5"))
    DB_PATH = os.getenv("DB_PATH")


settings = Settings()