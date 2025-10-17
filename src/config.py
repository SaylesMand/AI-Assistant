import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    QDRANT_PATH = os.getenv("QDRANT_PATH", "data/qdrant")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "qdrant_rag")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    TOP_K = int(os.getenv("TOP_K", "3"))

settings = Settings()