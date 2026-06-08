import sys

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from codedoctor.cli import parse_args
from codedoctor.config import Config
from codedoctor.doctor.prompts import prompt
from codedoctor.state import DoctorState
from codedoctor.doctor.tools import edit_file, list_all_files, open_file
from codedoctor.utils import run_tests
import re


def main():
    args = parse_args()

    cfg = Config(
        args.root_dir,
        args.search_dir,
        args.test_dir,
        args.model,
        args.max_retries,
        args.ignore,
        not args.include_dot,
    )

    model = ChatGoogleGenerativeAI(model=cfg.model_name)

    tools = [list_all_files, open_file, edit_file]
    model_with_tools = model.bind_tools(tools)

    def node(state: DoctorState):
        response = model_with_tools.invoke(
            ([SystemMessage(content=prompt)] + state.get("messages"))
        )
        return {"messages": response}

    tool_node = ToolNode(tools)

    def should_test(state: DoctorState):
        last_msg: ToolMessage = state.get("messages")[-1]
        if last_msg.name in ("list_all_files", "open_file"):
            return "model"
        return "tester"

    def test_node(state: DoctorState):
        test_result = run_tests(cfg.test_dir)
        if "EXIT_CODE:0" in test_result:
            ctx = "All tests passed successfully! Do not call any more tools. You are completely done. Provide your final text summary now."
            return {"messages": [HumanMessage(content=ctx)]}
        return {
            "messages": [HumanMessage(content=test_result)],
            "retry_count": state.get("retry_count", 0) + 1,
        }

    def should_continue(state: DoctorState):
        if state.get("retry_count") > state.get("cfg").max_retries:
            return END
        if state.get("messages")[-1].tool_calls:
            return "tool"
        return END

    builder = StateGraph(DoctorState)
    builder.add_node("model", node)
    builder.add_node("tool", tool_node)
    builder.add_node("tester", test_node)
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", should_continue, ["tool", END])
    builder.add_conditional_edges("tool", should_test, ["model", "tester"])
    builder.add_edge("tester", "model")

    graph = builder.compile()

    pre_test = run_tests(cfg.test_dir)
    if "passed" in pre_test:
        print("All tests are passing. Exiting")
        sys.exit(0)

    failed = re.findall(r"^FAILED\s+(.+)$", pre_test, re.MULTILINE)
    summary = "\n".join(failed)

    p = f"User's request: {args.prompt}\nCurrent test failures:\n{summary}\nFull test result:\n{pre_test}"

    messages = [HumanMessage(content=p)]
    graph_input = {"messages": messages, "cfg": cfg, "retry_count": 0}

    print(f"Running CodeDoctor on the directory:  {cfg.search_dir}\n")

    for chunk in graph.stream(graph_input, stream_mode="updates", version="v2"):
        if chunk["type"] == "updates":
            for node_name, state in chunk["data"].items():
                if node_name == "model":
                    m = state.get("messages").content
                    tool_call = state.get("messages").tool_calls

                    if m:
                        print(f"\n[DOCTOR] :  {m[0].get('text')}")

                    if tool_call:
                        tool = tool_call[0]
                        tool_name = tool.get("name")
                        tool_args = tool.get("args")

                        if tool_name == "list_all_files":
                            print("Doctor is understanding the directory...")

                        if tool_name == "open_file":
                            print(f"Doctor is reading {tool_args.get('path')}")

                        if tool_name == "edit_file":
                            print(f"Doctor is editing {tool_args.get('path')}")

                if node_name == "tool":
                    m = state.get("messages")[0]
                    if "Error:" in m.content:
                        print(m)
                        print(f"Error: Tool {m.name} failed.")
                    else:
                        print(f"Tool {m.name} executed successfully.")

                if node_name == "tester":
                    m: str = state.get("messages")[0].content
                    if "passed" in m:
                        print("All tests passed successfully")
                    else:
                        print("Following Tests Failed")
                        failed = re.findall(r"^FAILED\s+(.+)$", m, re.MULTILINE)
                        for line in failed:
                            print(line)
                        print()


if __name__ == "__main__":
    main()
