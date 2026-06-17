from asyncio import Queue, create_task, to_thread, wait_for
from collections.abc import AsyncIterable
from fastapi import FastAPI
from pathlib import Path
from fastapi.sse import EventSourceResponse, ServerSentEvent
from codedoctor.cli import (
    get_toml_data,
    prepare_exclude_dot_from_toml,
    prepare_ignore_set_from_toml,
)
from codedoctor.config import Config

from codedoctor.doctor.main import (
    create_graph as doctor_create_graph,
    prepare_graph_input as doctor_prepare_graph_input,
    run_graph as doctor_run_graph,
    should_run_graph as doctor_should_run_graph,
)

from codedoctor.engineer.main import (
    create_graph as engineer_create_graph,
    run_graph as engineer_run_graph,
)

app = FastAPI()


@app.post("/api/doctor", response_class=EventSourceResponse)
async def post_doctor(root_dir: str, prompt: str) -> AsyncIterable[ServerSentEvent]:
    path_to_toml = Path(root_dir) / "pyproject.toml"
    toml_data = get_toml_data(path_to_toml)
    ignore_set = prepare_ignore_set_from_toml(toml_data)
    exclude_dot = prepare_exclude_dot_from_toml(toml_data)
    cfg = Config(
        root_dir,
        toml_data.get("search_dir"),
        toml_data.get("test_dir"),
        toml_data.get("strong_model"),
        toml_data.get("weak_model"),
        toml_data.get("max_retries"),
        ignore_set,
        exclude_dot,
    )
    should_continue, pre_test_result = doctor_should_run_graph(cfg)
    if not should_continue:
        yield ServerSentEvent(data="All tests passing. Exiting.", event="done")
        return

    q = Queue()

    def callback(message: str):
        q.put_nowait(message)

    cfg.subscribe(callback)

    graph = doctor_create_graph(cfg)
    graph_inputs = doctor_prepare_graph_input(pre_test_result, prompt, cfg)
    graph_task = create_task(to_thread(doctor_run_graph, graph, graph_inputs, cfg))

    try:
        while not graph_task.done() or not q.empty():
            try:
                data = await wait_for(q.get(), 1)
                yield ServerSentEvent(event="log", data=data)
                q.task_done()
            except TimeoutError:
                continue
        await graph_task
        yield ServerSentEvent(event="done", data="Task has been completed")
    except Exception as e:
        yield ServerSentEvent(event="error", data=f"Exception :  {str(e)}")


@app.post("/api/engineer", response_class=EventSourceResponse)
async def post_engineer(root_dir: str, prompt: str) -> AsyncIterable[ServerSentEvent]:
    path_to_toml = Path(root_dir) / "pyproject.toml"
    toml_data = get_toml_data(path_to_toml)
    ignore_set = prepare_ignore_set_from_toml(toml_data)
    exclude_dot = prepare_exclude_dot_from_toml(toml_data)
    cfg = Config(
        root_dir,
        toml_data.get("search_dir"),
        toml_data.get("test_dir"),
        toml_data.get("strong_model"),
        toml_data.get("weak_model"),
        toml_data.get("max_retries"),
        ignore_set,
        exclude_dot,
    )
    q = Queue()

    def callback(message: str):
        q.put_nowait(message)

    cfg.subscribe(callback)

    graph = engineer_create_graph(cfg)
    graph_task = create_task(to_thread(engineer_run_graph, graph, prompt, cfg))

    try:
        while not graph_task.done() or not q.empty():
            try:
                data = await wait_for(q.get(), 1)
                yield ServerSentEvent(event="log", data=data)
                q.task_done()
            except TimeoutError:
                continue
        await graph_task
        yield ServerSentEvent(event="done", data="Task has been completed")
    except Exception as e:
        yield ServerSentEvent(event="error", data=f"Exception :  {str(e)}")
