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

    pre_test_result = run_tests(cfg.test_dir)
    if "EXIT_CODE:0" in pre_test_result:
        print("All tests are passing. Exiting")
        sys.exit(0)

    model_doctor = ChatGoogleGenerativeAI(model=cfg.model_name)

    tools_doctor = [list_all_files, open_file, edit_file]
    model_doctor_with_tools = model_doctor.bind_tools(tools_doctor)

    def node_doctor(state: DoctorState):
        response = model_doctor_with_tools.invoke(
            ([SystemMessage(content=prompt)] + state.get("messages"))
        )
        return {"messages": response}

    node_tool = ToolNode(tools_doctor, handle_tool_errors=True)

    def node_test(state: DoctorState):
        test_result = run_tests(cfg.test_dir)
        if "EXIT_CODE:0" in test_result:
            ctx = "All tests passed successfully! Do not call any more tools. You are completely done. Provide your final text summary now."
            return {"messages": [HumanMessage(content=ctx)]}
        return {
            "messages": [HumanMessage(content=test_result)],
            "retry_count": state.get("retry_count", 0) + 1,
        }

    def check_should_test(state: DoctorState):
        last_msg: ToolMessage = state.get("messages")[-1]
        if last_msg.name in ("list_all_files", "open_file"):
            return "node_doctor"
        return "node_test"

    def check_should_continue(state: DoctorState):
        if state.get("retry_count") > state.get("cfg").max_retries:
            return END
        if state.get("messages")[-1].tool_calls:
            return "node_tool"
        return END

    graph_builder = StateGraph(DoctorState)
    graph_builder.add_node("node_doctor", node_doctor)
    graph_builder.add_node("node_tool", node_tool)
    graph_builder.add_node("node_test", node_test)
    graph_builder.add_edge(START, "node_doctor")
    graph_builder.add_conditional_edges(
        "node_doctor", check_should_continue, ["node_tool", END]
    )
    graph_builder.add_conditional_edges(
        "node_tool", check_should_test, ["node_doctor", "node_test"]
    )
    graph_builder.add_edge("node_test", "node_doctor")

    graph = graph_builder.compile()

    failed = re.findall(r"^FAILED\s+(.+)$", pre_test_result, re.MULTILINE)
    summary = "\n".join(failed)

    final_prompt = f"User's request: {args.prompt}\nCurrent test failures:\n{summary}\nFull test result:\n{pre_test_result}"

    messages = [HumanMessage(content=final_prompt)]
    graph_input = {"messages": messages, "cfg": cfg, "retry_count": 0}

    print(f"Running CodeDoctor on the directory:  {cfg.search_dir}\n")

    for chunk in graph.stream(graph_input, stream_mode="updates", version="v2"):
        if chunk["type"] == "updates":
            for node_name, state in chunk["data"].items():
                if node_name == "node_doctor":
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

                if node_name == "node_tool":
                    m = state.get("messages")[0]
                    if getattr(m, "status", None) == "error":
                        print(f"Error: Tool {m.name} failed with \n{m.content}")
                    else:
                        print(f"Tool {m.name} executed successfully.")

                if node_name == "node_test":
                    m: str = state.get("messages")[0].content
                    if "EXIT_CODE:0" in m:
                        print("All tests passed successfully")
                    else:
                        print("Following Tests Failed")
                        failed = re.findall(r"^FAILED\s+(.+)$", m, re.MULTILINE)
                        for line in failed:
                            print(line)
                        print()


if __name__ == "__main__":
    main()
