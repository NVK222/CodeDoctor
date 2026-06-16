import sys
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from codedoctor.cli import initialize_config
from codedoctor.config import Config
from codedoctor.doctor.prompts import prompt
from codedoctor.state import DoctorState
from codedoctor.doctor.tools import edit_file, list_all_files, open_file
from codedoctor.utils import print_to_terminal, run_tests
import re


def prepare_graph_input(pre_test_result: str, user_prompt: str, cfg: Config):
    failed = re.findall(r"^FAILED\s+(.+)$", pre_test_result, re.MULTILINE)
    summary = "\n".join(failed)

    final_prompt = f"User's request: {user_prompt}\nCurrent test failures:\n{summary}\nFull test result:\n{pre_test_result}"

    messages = [HumanMessage(content=final_prompt)]
    return {"messages": messages, "cfg": cfg, "retry_count": 0}


def run_graph(
    graph: CompiledStateGraph[DoctorState, None, DoctorState, DoctorState],
    graph_input: dict[str, list[HumanMessage] | Config | int],
    cfg: Config,
):
    cfg.notify(f"Running CodeDoctor on the directory:  {cfg.search_dir}\n")

    for chunk in graph.stream(graph_input, stream_mode="updates", version="v2"):
        if chunk["type"] == "updates":
            for node_name, state in chunk["data"].items():
                if node_name == "node_doctor":
                    m = state.get("messages").content
                    tool_call = state.get("messages").tool_calls

                    if m:
                        cfg.notify(f"\n[DOCTOR] :  {m[0].get('text')}")

                    if tool_call:
                        tool = tool_call[0]
                        tool_name = tool.get("name")
                        tool_args = tool.get("args")

                        if tool_name == "list_all_files":
                            cfg.notify("Doctor is understanding the directory...")

                        if tool_name == "open_file":
                            cfg.notify(f"Doctor is reading {tool_args.get('path')}")

                        if tool_name == "edit_file":
                            cfg.notify(f"Doctor is editing {tool_args.get('path')}")

                if node_name == "node_tool":
                    m = state.get("messages")[0]
                    if getattr(m, "status", None) == "error":
                        cfg.notify(f"Error: Tool {m.name} failed with \n{m.content}")
                    else:
                        cfg.notify(f"Tool {m.name} executed successfully.")

                if node_name == "node_test":
                    m: str = state.get("messages")[0].content
                    if "EXIT_CODE:0" in m:
                        cfg.notify("All tests passed successfully")
                    else:
                        cfg.notify("Following Tests Failed")
                        failed = re.findall(r"^FAILED\s+(.+)$", m, re.MULTILINE)
                        for line in failed:
                            cfg.notify(line)
                        cfg.notify("")


def should_run_graph(cfg: Config) -> tuple[bool, str]:
    pre_test_result = run_tests(cfg.test_dir)
    if "EXIT_CODE:0" in pre_test_result:
        cfg.notify("All tests are passing. Exiting")
        return (False, "")
    return (True, pre_test_result)


def create_graph(cfg: Config):
    model_doctor = ChatGoogleGenerativeAI(model=cfg.strong_model_name)

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

    return graph


def main():
    cfg, user_prompt = initialize_config()
    cfg.subscribe(print_to_terminal)

    should_continue, pre_test_result = should_run_graph(cfg)
    if not should_continue:
        sys.exit(0)

    graph = create_graph(cfg)
    graph_inputs = prepare_graph_input(pre_test_result, user_prompt, cfg)
    run_graph(graph, graph_inputs, cfg)


if __name__ == "__main__":
    main()
