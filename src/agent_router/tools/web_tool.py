from langchain_community.tools import DuckDuckGoSearchRun


class WebTool:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()

    def run(self, query: str) -> str:
        response = self.search.invoke(query)
        return response
