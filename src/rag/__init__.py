from .loader import DocumentLoader
from .splitter import DocumentSplitter
from .indexing import Index
from .pipeline import RAGPipeline
from src.config import settings


def build_rag_pipeline() -> RAGPipeline:
    api_key = settings.MISTRAL_API_KEY
    loader = DocumentLoader("data/data_copy2.json")
    splitter = DocumentSplitter(chunk_size=settings.CHUNK_SIZE)
    docs = splitter.split_docs(loader.load())

    index = Index(
        api_key=api_key,
        path=settings.QDRANT_PATH,
        collection_name=settings.QDRANT_COLLECTION,
    )
    vector_store = index.add_documents(docs)
    return RAGPipeline(vector_store, api_key=api_key, top_k=settings.TOP_K)
