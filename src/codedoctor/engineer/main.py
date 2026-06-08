from pathlib import Path
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import ToolNode
from codedoctor.config import Config
from codedoctor.engineer.prompts import prompt
from codedoctor.engineer.tools import (
    create_test,
    edit_test,
    list_src,
    list_tests,
    open_src,
)
from codedoctor.state import EngineerState
from codedoctor.utils import run_tests
import re

cfg = Config(Path("/home/nkumar/projects/CodeDoctor/"))

engineer = ChatGoogleGenerativeAI(model=cfg.model_name)

tools = [create_test, list_tests, list_src, edit_test, open_src]
engineer_with_tools = engineer.bind_tools(tools)


def engineer_node(state: EngineerState):
    response = engineer_with_tools.invoke(
        ([SystemMessage(content=prompt)]) + state.get("messages")
    )
    return {"messages": response}


tool_node = ToolNode(tools)


def test_node(state: EngineerState):
    test_result = run_tests(cfg.test_dir)
    if "EXIT_CODE:1" in test_result:
        ctx = f"There are some issues in the test code. Here is the test output: {test_result}"
        return {"messages": [HumanMessage(content=ctx)]}
    ctx = f"All tests passed successfully!\n{test_result}"
    return {"messages": [HumanMessage(content=ctx)]}


def should_continue(state: EngineerState):
    last_msg: AIMessage = state.get("messages")[-1]
    if last_msg.tool_calls:
        return "tool_node"
    return "test_node"


def should_end(state: EngineerState):
    last_msg: HumanMessage = state.get("messages")[-1].content
    if "passed" in last_msg:
        return END
    if state.get("retry_count") >= state.get("cfg").max_retries:
        return END
    return "engineer"


builder = StateGraph(EngineerState)
builder.add_node("engineer", engineer_node)
builder.add_node("test_node", test_node)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "engineer")
builder.add_conditional_edges("engineer", should_continue, ["tool_node", "test_node"])
builder.add_edge("tool_node", "engineer")
builder.add_conditional_edges("test_node", should_end, [END, "engineer"])

graph = builder.compile()

print(f"Running Engineer on {cfg.root_dir}")

messages = [HumanMessage(content="Add tests for the file utils.py")]
for chunk in graph.stream(
    {"messages": messages, "cfg": cfg, "retry_count": 0},
    stream_mode="updates",
    version="v2",
):
    if chunk["type"] == "updates":
        for node_name, state in chunk["data"].items():
            if node_name == "engineer":
                m = state.get("messages").content
                tool_call = state.get("messages").tool_calls

                if m:
                    print(f"\n[ENGINEER] :  {m[0].get('text')}")

                if tool_call:
                    tool = tool_call[0]
                    tool_name = tool.get("name")
                    tool_args = tool.get("args")

                    if tool_name == "list_tests":
                        print("Doctor is understanding the tests directory...")
                    if tool_name == "list_src":
                        print("Doctor is understanding the src directory...")

                    if tool_name == "create_test":
                        print(
                            f"Doctor is creating test for {tool_args.get('src_path')}"
                        )

                    if tool_name == "edit_test":
                        print(f"Doctor is editing test {tool_args.get('path')}")

            if node_name == "tool_node":
                m = state.get("messages")[0]
                # Need more robust error checking
                if "Error:" in m.content:
                    print(f"Error: Tool {m.name} failed.")
                else:
                    print(f"Tool {m.name} executed successfully.")

            if node_name == "test_node":
                m: str = state.get("messages")[0].content
                if "passed" in m:
                    print("ALL TESTS PASSED SUCCESSFULLY")
                else:
                    print("\nFollowing Tests Failed\n")
                    failed = re.findall(r"^FAILED\s+(.+)$", m, re.MULTILINE)
                    for line in failed:
                        print(line)
                    print("\n\n")
