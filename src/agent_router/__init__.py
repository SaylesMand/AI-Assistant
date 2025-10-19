from src.agent_router.router_agent import RouterAgent
from src.utils.models.llm_factory import create_chat_model


def load_router_agent():
    llm = create_chat_model()
    agent_router = RouterAgent(llm=llm)
    return agent_router
