from typing import TypedDict

from langgraph.graph.message import MessagesState


class InputSchema(TypedDict):
    prompt: str


class State(MessagesState):
    prompt: str
    retry_count: int
    max_retries: int
