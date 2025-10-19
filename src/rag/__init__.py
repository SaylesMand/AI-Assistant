from .loader import DocumentLoader
from .splitter import DocumentSplitter
from .indexing import Index
from .pipeline import RAGPipeline
from src.config import settings
from src.utils.models.llm_factory import create_chat_model, create_embedding_model


def build_rag_pipeline() -> RAGPipeline:
    llm = create_chat_model()
    embeddings = create_embedding_model()    
    
    loader = DocumentLoader(settings.DATA_PATH)
    splitter = DocumentSplitter(chunk_size=settings.CHUNK_SIZE)
    docs = splitter.split_docs(loader.load())

    index = Index(        
        path=settings.QDRANT_PATH,
        collection_name=settings.QDRANT_COLLECTION,
        embeddings=embeddings,
    )
    vector_store = index.add_documents(docs)
    return RAGPipeline(vector_store, llm=llm, top_k=settings.TOP_K)
