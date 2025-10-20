from src.rag import load_rag_agent


class RAGTool:
    def __init__(self):
        self.rag_agent = load_rag_agent()
    
    def run(self, query: str) -> str:
        return self.rag_agent.ask(query)