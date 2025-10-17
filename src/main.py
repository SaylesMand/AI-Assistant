# from crawler import BaseCrawler
# from time import time


# url = "https://help.ptsecurity.com/ru-RU/projects/mp10/27.4/help/922069771"
# base_crawler = BaseCrawler(url=url)

# start = time()
# base_crawler.run_crawler(url, max_depth=0, max_concurrent=5)
# end = time()
# print(f"\nПрошло {end - start:.2f} секунд\n")


from rag.loader import DocumentLoader
from rag.splitter import DocumentSplitter
from rag.indexing import Index
from rag.pipeline import RAGPipeline

from config import settings

if __name__ == "__main__":
    api_key = settings.MISTRAL_API_KEY
    loader = DocumentLoader("data/data_copy2.json")
    splitter = DocumentSplitter(chunk_size=settings.CHUNK_SIZE)
    docs = splitter.split_docs(loader.load())

    index = Index(api_key=api_key, path=settings.QDRANT_PATH, collection_name=settings.QDRANT_COLLECTION)
    vector_store = index.add_documents(docs)

    rag = RAGPipeline(vector_store, api_key=api_key, top_k=settings.TOP_K)

    question = "Из чего состоит архитектура MaxPatrol 10?"
    print(rag.ask(question))