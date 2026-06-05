from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from prompts import prompt
from state import State
from tools import edit_file, list_files, open_file
from utils import run_tests

load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
tools = [list_files, open_file, edit_file]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)


def node(state: State):
    response = model_with_tools.invoke(
        ([SystemMessage(content=prompt)] + state.get("messages"))
    )
    return {"messages": response, "retry_count": state.get("retry_count", 0) + 1}


def tool_node(state: State):
    result = []
    for tool_call in state.get("messages")[-1].tool_calls:
        tool = tools_by_name[tool_call.get("name")]
        output = tool.invoke(tool_call.get("args"))
        result.append(
            ToolMessage(
                name=tool_call.get("name"),
                content=output,
                tool_call_id=tool_call.get("id"),
            )
        )
    return {"messages": result}


def should_test(state: State):
    last_msg: ToolMessage = state.get("messages")[-1]
    if last_msg.name in ("list_files", "open_file"):
        return "model"
    return "tester"


def test_node(state: State):
    test_result = run_tests()
    if "All tests passed successfully" in test_result:
        ctx = "All tests passed successfully! Do not call any more tools. You are completely done. Provide your final text summary now."
    else:
        ctx = test_result
    return {"messages": [HumanMessage(content=ctx)]}


def should_continue(state: State):
    if state.get("retry_count") > 50:
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

messages = [HumanMessage(content="Fix the division by zero error.")]
messages = graph.invoke({"messages": messages})
for m in messages.get("messages"):
    m.pretty_print()
