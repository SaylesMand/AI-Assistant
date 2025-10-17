from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from utils import hash_content


class DocumentSplitter:
    """Разделение документа на чанки с помощью RecursiveCharacterTextSplitter"""

    def __init__(self, chunk_size: int = 1000, overlap_ratio: float = 0.1):
        self.chunk_size = chunk_size
        self.overlap = int(chunk_size * overlap_ratio)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=self.overlap,
            separators=["\n\n", "\n", ".", "!", "?"],
            strip_whitespace=True,
        )

    def split_docs(self, docs: list[Document]) -> list[Document]:
        """Разделить список LangChain Document на небольшие чанки и проверить на дубликаты"""
        processed_docs = []
        for doc in docs:
            chunks = self.text_splitter.split_text(doc.page_content)
            content_hash = hash_content(doc.page_content)

            for i, chunk_text in enumerate(chunks):
                metadata = {**doc.metadata}
                metadata.update(
                    {
                        "chunk_id": i,
                        "source_hash": content_hash,  # хэш исходного документа
                    }
                )
                processed_docs.append(
                    Document(page_content=chunk_text, metadata=metadata)
                )

        return processed_docs
