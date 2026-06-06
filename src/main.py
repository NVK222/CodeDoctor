from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from cli import parse_args
from config import Config
from prompts import prompt
from state import State
from tools import edit_file, list_files, open_file
from utils import run_tests

args = parse_args()

cfg = Config(
    args.model,
    args.max_retries,
    args.ignore,
    not args.include_dot,
    args.root_dir,
    args.search_dir,
    args.test_dir,
)
model = ChatGoogleGenerativeAI(model=cfg.model_name)

tools = [list_files, open_file, edit_file]
model_with_tools = model.bind_tools(tools)


def node(state: State):
    response = model_with_tools.invoke(
        ([SystemMessage(content=prompt)] + state.get("messages"))
    )
    return {"messages": response}


tool_node = ToolNode(tools)


def should_test(state: State):
    last_msg: ToolMessage = state.get("messages")[-1]
    if last_msg.name in ("list_files", "open_file"):
        return "model"
    return "tester"


def test_node(state: State):
    test_result = run_tests(cfg.test_dir)
    if "All tests passed successfully" in test_result:
        ctx = "All tests passed successfully! Do not call any more tools. You are completely done. Provide your final text summary now."
        return {"messages": [HumanMessage(content=ctx)]}
    return {
        "messages": [HumanMessage(content=test_result)],
        "retry_count": state.get("retry_count", 0) + 1,
    }


def should_continue(state: State):
    if state.get("retry_count") > state.get("cfg").max_retries:
        return END
    if state.get("messages")[-1].tool_calls:
        return "tool"
    return END


builder = StateGraph(State)
builder.add_node("model", node)
builder.add_node("tool", tool_node)
builder.add_node("tester", test_node)
builder.add_edge(START, "model")
builder.add_conditional_edges("model", should_continue, ["tool", END])
builder.add_conditional_edges("tool", should_test, ["model", "tester"])
builder.add_edge("tester", "model")

graph = builder.compile()

messages = [HumanMessage(content=args.prompt)]
messages = graph.invoke({"messages": messages, "cfg": cfg, "retry_count": 0})
for m in messages.get("messages"):
    m.pretty_print()
