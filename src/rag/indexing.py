from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.config import settings


class Index:
    """Управляет созданием Qdrant коллекции и хранением векторов."""

    def __init__(self, path: str, collection_name: str, embeddings: Embeddings):
        self.path = path
        self.collection_name = collection_name
        self.client = QdrantClient(url=settings.QDRANT_URL)
        # self.client = QdrantClient(path=settings.QDRANT_PATH)
        self.embeddings = embeddings

    def initialize(self):
        """Создаёт коллекцию, если она не существует."""
        vector_size = len(self.embeddings.embed_query("test"))
        self.collection_name = f"{settings.QDRANT_COLLECTION}_{settings.LLM_MODE}_{vector_size}"
        # vector_size = 1024
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size, distance=models.Distance.COSINE, on_disk=True
                ),
            )

    def _get_existing_hashes(self) -> set[str]:
        """Загружает все существующие source_hash из коллекции Qdrant"""
        try:
            existing_hashes = set()
            scroll_offset = None

            while True:
                points, scroll_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    with_payload=True,
                    limit=1000,
                    offset=scroll_offset,
                )
                for p in points:
                    payload = p.payload or {}
                    if "source_hash" in payload["metadata"]:
                        existing_hashes.add(payload["metadata"]["source_hash"])
                if scroll_offset is None:
                    break

            return existing_hashes

        except Exception:
            return set()

    def add_documents(self, docs: list[Document]):
        """Добавляет документы в Qdrant."""
        self.initialize()

        existing_hashes = self._get_existing_hashes()
        new_docs = [
            doc
            for doc in docs
            if doc.metadata.get("source_hash") not in existing_hashes
        ]

        if not new_docs:
            print(
                f"[INFO] Все документы уже добавлены в коллекцию '{self.collection_name}'. Пропуск."
            )
            return QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
            )

        print(
            f"[INFO] В коллекции  '{self.collection_name}' существует {len(existing_hashes)} документов."
        )
        print(
            f"[INFO] Добавляю {len(new_docs)} новых документов в коллекцию '{self.collection_name}'..."
        )
        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
        vector_store.add_documents(new_docs)

        return vector_store
