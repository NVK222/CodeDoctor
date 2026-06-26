from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from codedoctor.config import Config
from codedoctor.engineer.prompts import prompt_auditor, prompt_engineer, prompt_summary
from codedoctor.engineer.tools import (
    add_test,
    create_test,
    edit_test,
    list_src,
    list_tests,
    open_src,
)
from codedoctor.state import EngineerState
from codedoctor.utils import is_test_successful, run_tests


def create_graph(cfg: Config):
    model_engineer = ChatGoogleGenerativeAI(model=cfg.strong_model_name)
    model_auditor = ChatGoogleGenerativeAI(model=cfg.weak_model_name)

    tools_engineer = [create_test, list_tests, list_src, edit_test, open_src, add_test]
    model_engineer_with_tools = model_engineer.bind_tools(tools_engineer)

    async def node_engineer(state: EngineerState):
        response = await model_engineer_with_tools.ainvoke(
            ([SystemMessage(content=prompt_engineer)]) + state.get("messages")
        )
        return {"messages": response}

    node_tool = ToolNode(tools_engineer, handle_tool_errors=True)

    async def node_test(state: EngineerState):
        cfg.notify("Making sure everything is alright...")
        test_result = await run_tests(cfg.test_dir)
        return {"messages": [HumanMessage(content=test_result)]}

    async def node_auditor(state: EngineerState):
        last_msg: HumanMessage = state.get("messages")[-1]
        response = await model_auditor.ainvoke(
            ([SystemMessage(content=prompt_auditor)] + [last_msg.content])
        )

        if response.text.strip().upper() == "ENGINEER":
            return {
                "retry_count": state.get("retry_count") + 1,
                "auditor_decision": "ENGINEER",
            }
        return {"auditor_decision": "END"}

    async def node_summary(state: EngineerState):
        response = await model_engineer.ainvoke(
            (state.get("messages") + [HumanMessage(content=prompt_summary)])
        )

        return {"messages": response}

    def check_should_test(state: EngineerState):
        last_msg: AIMessage = state.get("messages")[-1]
        if last_msg.tool_calls:
            return "node_tool"
        return "node_test"

    def check_test_results(state: EngineerState):
        last_msg: HumanMessage = state.get("messages")[-1]
        if is_test_successful(last_msg.text, ["EXIT_CODE:0"]):
            return "node_summary"
        if state.get("retry_count") >= cfg.max_retries:
            return "node_summary"
        return "node_auditor"

    def check_should_continue(state: EngineerState):
        if state.get("auditor_decision") == "ENGINEER":
            return "node_engineer"
        return "node_summary"

    builder = StateGraph(EngineerState)
    builder.add_node("node_engineer", node_engineer)
    builder.add_node("node_test", node_test)
    builder.add_node("node_tool", node_tool)
    builder.add_node("node_auditor", node_auditor)
    builder.add_node("node_summary", node_summary)

    builder.add_edge(START, "node_engineer")
    builder.add_conditional_edges(
        "node_engineer", check_should_test, ["node_tool", "node_test"]
    )
    builder.add_edge("node_tool", "node_engineer")
    builder.add_conditional_edges(
        "node_test", check_test_results, ["node_summary", "node_auditor"]
    )
    builder.add_conditional_edges(
        "node_auditor", check_should_continue, ["node_summary", "node_engineer"]
    )
    builder.add_edge("node_summary", END)

    graph = builder.compile()
    return graph


async def run_graph(
    graph: CompiledStateGraph[EngineerState, None, EngineerState, EngineerState],
    user_prompt: str,
    cfg: Config,
):
    cfg.notify(f"Running Engineer on {cfg.test_dir}")

    messages = [HumanMessage(content=user_prompt)]
    graph_input = {"messages": messages, "cfg": cfg, "retry_count": 0}
    async for chunk in graph.astream(
        graph_input,
        stream_mode="updates",
        version="v2",
    ):
        if chunk["type"] == "updates":
            for node_name, state in chunk["data"].items():
                if node_name == "node_engineer":
                    tool_call = state.get("messages").tool_calls

                    if tool_call:
                        tool = tool_call[0]
                        tool_name = tool.get("name")
                        tool_args = tool.get("args")

                        if tool_name == "list_tests":
                            cfg.notify(
                                "Engineer is understanding the tests directory..."
                            )
                        if tool_name == "list_src":
                            cfg.notify("Engineer is understanding the src directory...")

                        if tool_name == "create_test":
                            cfg.notify(
                                f"Engineer is creating test for {tool_args.get('src_path')}"
                            )

                        if tool_name == "edit_test":
                            cfg.notify(
                                f"Engineer is editing test {tool_args.get('path')}"
                            )

                        if tool_name == "add_test":
                            cfg.notify(
                                f"Engineer is adding new tests to {tool_args.get('path')}"
                            )

                if node_name == "node_tool":
                    m: ToolMessage = state.get("messages")[0]
                    if not isinstance(m, ToolMessage):
                        return
                    if getattr(m, "status", None) == "error":
                        cfg.notify(m.content)
                        cfg.notify(f"Error: Tool {m.name} failed with : \n{m.content} ")

                if node_name == "node_summary":
                    m: AIMessage = state.get("messages")
                    cfg.notify(m.text)
