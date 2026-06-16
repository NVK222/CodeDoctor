from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from codedoctor.cli import initialize_config
from codedoctor.config import Config
from codedoctor.engineer.prompts import prompt_auditor, prompt_engineer
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


def create_graph(cfg: Config):
    model_engineer = ChatGoogleGenerativeAI(model=cfg.strong_model_name)
    model_auditor = ChatGoogleGenerativeAI(model=cfg.weak_model_name)

    tools_engineer = [create_test, list_tests, list_src, edit_test, open_src]
    model_engineer_with_tools = model_engineer.bind_tools(tools_engineer)

    def node_engineer(state: EngineerState):
        response = model_engineer_with_tools.invoke(
            ([SystemMessage(content=prompt_engineer)]) + state.get("messages")
        )
        return {"messages": response}

    node_tool = ToolNode(tools_engineer, handle_tool_errors=True)

    def node_test(state: EngineerState):
        test_result = run_tests(cfg.test_dir)
        if "EXIT_CODE:1" in test_result:
            ctx = f"There are some issues in the test code. Here is the test output: {test_result}"
            return {"messages": [HumanMessage(content=ctx)]}
        return {"messages": [HumanMessage(content=test_result)]}

    def check_should_test(state: EngineerState):
        last_msg: AIMessage = state.get("messages")[-1]
        if last_msg.tool_calls:
            return "node_tool"
        return "node_test"

    def check_should_continue(state: EngineerState):
        last_msg: HumanMessage = state.get("messages")[-1].text
        if "EXIT_CODE:0" in last_msg:
            return END
        if state.get("retry_count") >= state.get("cfg").max_retries:
            return END
        response = model_auditor.invoke(
            ([SystemMessage(content=prompt_auditor)] + [last_msg])
        )

        if response.text.upper() == "ENGINEER":
            return "node_engineer"
        else:
            return END

    builder = StateGraph(EngineerState)
    builder.add_node("node_engineer", node_engineer)
    builder.add_node("node_test", node_test)
    builder.add_node("node_tool", node_tool)

    builder.add_edge(START, "node_engineer")
    builder.add_conditional_edges(
        "node_engineer", check_should_test, ["node_tool", "node_test"]
    )
    builder.add_edge("node_tool", "node_engineer")
    builder.add_conditional_edges(
        "node_test", check_should_continue, [END, "node_engineer"]
    )

    graph = builder.compile()
    return graph


def run_graph(
    graph: CompiledStateGraph[EngineerState, None, EngineerState, EngineerState],
    user_prompt: str,
    cfg: Config,
):
    print(f"Running Engineer on {cfg.test_dir}")

    messages = [HumanMessage(content=user_prompt)]
    graph_input = {"messages": messages, "cfg": cfg, "retry_count": 0}
    for chunk in graph.stream(
        graph_input,
        stream_mode="updates",
        version="v2",
    ):
        if chunk["type"] == "updates":
            for node_name, state in chunk["data"].items():
                if node_name == "node_engineer":
                    m = state.get("messages").content
                    tool_call = state.get("messages").tool_calls

                    if m:
                        print(f"\n[ENGINEER] :  {m[0].get('text')}")

                    if tool_call:
                        tool = tool_call[0]
                        tool_name = tool.get("name")
                        tool_args = tool.get("args")

                        if tool_name == "list_tests":
                            print("Engineer is understanding the tests directory...")
                        if tool_name == "list_src":
                            print("Engineer is understanding the src directory...")

                        if tool_name == "create_test":
                            print(
                                f"Engineer is creating test for {tool_args.get('src_path')}"
                            )

                        if tool_name == "edit_test":
                            print(f"Engineer is editing test {tool_args.get('path')}")

                if node_name == "node_tool":
                    m = state.get("messages")[0]
                    if getattr(m, "status", None) == "error":
                        print(f"Error: Tool {m.name} failed with : \n{m.content} ")
                    else:
                        print(f"Tool {m.name} executed successfully.")

                if node_name == "node_test":
                    m: str = state.get("messages")[0].content
                    if "EXIT_CODE:0" in m:
                        print("All tests passed successfully")
                    else:
                        print("\nFollowing Tests Failed\n")
                        failed = re.findall(r"^FAILED\s+(.+)$", m, re.MULTILINE)
                        for line in failed:
                            print(line)
                        print("\n\n")


def main():
    cfg, user_prompt = initialize_config()
    graph = create_graph(cfg)
    run_graph(graph, user_prompt, cfg)


if __name__ == "__main__":
    main()
