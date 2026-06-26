from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from codedoctor.config import Config
from codedoctor.doctor.prompts import prompt_doctor, prompt_summary
from codedoctor.state import DoctorState
from codedoctor.doctor.tools import edit_file, list_all_files, open_file
from codedoctor.utils import is_test_successful, run_tests
import re


def prepare_graph_input(pre_test_result: str, user_prompt: str, cfg: Config):
    failed = re.findall(r"^FAILED\s+(.+)$", pre_test_result, re.MULTILINE)
    summary = "\n".join(failed)

    final_prompt = f"User's request: {user_prompt}\nCurrent test failures:\n{summary}\nFull test result:\n{pre_test_result}"

    messages = [HumanMessage(content=final_prompt)]
    return {"messages": messages, "cfg": cfg, "retry_count": 0}


async def run_graph(
    graph: CompiledStateGraph[DoctorState, None, DoctorState, DoctorState],
    graph_input: dict[str, list[HumanMessage] | Config | int],
    cfg: Config,
):
    cfg.notify(f"Running CodeDoctor on the directory:  {cfg.search_dir}\n")

    async for chunk in graph.astream(graph_input, stream_mode="updates", version="v2"):
        if chunk["type"] == "updates":
            for node_name, state in chunk["data"].items():
                if node_name == "node_doctor":
                    tool_call = state.get("messages").tool_calls

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

                if node_name == "node_summary":
                    m = state.get("messages")
                    cfg.notify(m.text)


async def should_run_graph(cfg: Config) -> tuple[bool, str]:
    pre_test_result = await run_tests(cfg.test_dir)
    if is_test_successful(pre_test_result):
        cfg.notify("All tests are passing. Exiting")
        return (False, "")
    return (True, pre_test_result)


def create_graph(cfg: Config):
    model_doctor = ChatGoogleGenerativeAI(model=cfg.strong_model_name)

    tools_doctor = [list_all_files, open_file, edit_file]
    model_doctor_with_tools = model_doctor.bind_tools(tools_doctor)

    async def node_doctor(state: DoctorState):
        response = await model_doctor_with_tools.ainvoke(
            ([SystemMessage(content=prompt_doctor)] + state.get("messages"))
        )
        return {"messages": response}

    node_tool = ToolNode(tools_doctor, handle_tool_errors=True)

    async def node_test(state: DoctorState):
        test_result = await run_tests(cfg.test_dir)
        return {
            "messages": [HumanMessage(content=test_result)],
            "retry_count": state.get("retry_count", 0) + 1,
        }

    async def node_summary(state: DoctorState):
        response = await model_doctor.ainvoke(
            ([SystemMessage(content=prompt_summary)] + state.get("messages"))
        )
        return {"messages": response}

    # Checks whether we should call another tool or goto test node if no more tools need to be executed.
    def check_doctor_action(state: DoctorState):
        last_msg: AIMessage = state.get("messages")[-1]
        if last_msg.tool_calls:
            return "node_tool"
        return "node_test"

    def check_should_continue(state: DoctorState):
        last_msg = state.get("messages")[-1]
        if state.get("retry_count") >= state.get("cfg").max_retries:
            return "node_summary"
        if is_test_successful(last_msg.text):
            return "node_summary"
        return "node_doctor"

    graph_builder = StateGraph(DoctorState)
    graph_builder.add_node("node_doctor", node_doctor)
    graph_builder.add_node("node_tool", node_tool)
    graph_builder.add_node("node_test", node_test)
    graph_builder.add_node("node_summary", node_summary)

    graph_builder.add_edge(START, "node_doctor")
    graph_builder.add_conditional_edges(
        "node_doctor", check_doctor_action, ["node_tool", "node_test"]
    )
    graph_builder.add_edge("node_tool", "node_doctor")
    graph_builder.add_conditional_edges(
        "node_test", check_should_continue, ["node_summary", "node_doctor"]
    )
    graph_builder.add_edge("node_summary", END)

    graph = graph_builder.compile()

    return graph
