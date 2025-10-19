from src.rag import build_rag_pipeline


class RAGTool:
    def __init__(self):
        self.rag = build_rag_pipeline()
    
    def run(self, query: str) -> str:
        return self.rag.ask(query)