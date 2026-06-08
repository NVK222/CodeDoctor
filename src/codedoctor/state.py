from langgraph.graph.message import MessagesState
from codedoctor.config import Config


class DoctorState(MessagesState):
    retry_count: int
    cfg: Config


class EngineerState(MessagesState):
    cfg: Config
    retry_count: int
