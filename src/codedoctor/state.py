from langgraph.graph.message import MessagesState
from codedoctor.config import Config


class State(MessagesState):
    retry_count: int
    cfg: Config
