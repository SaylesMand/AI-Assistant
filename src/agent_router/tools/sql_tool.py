from src.sql_agent import load_sql_agent


class SQLTool:
    def __init__(self):
        self.sql_agent = load_sql_agent()
    
    def run(self, query: str) -> str:
        return self.sql_agent.ask(query)