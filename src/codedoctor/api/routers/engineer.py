from asyncio import Queue, create_task, to_thread, wait_for
from collections.abc import AsyncIterable
from pathlib import Path
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent
from codedoctor.api.schemas import EngineerRequest
from codedoctor.cli import (
    get_toml_data,
    prepare_exclude_dot_from_toml,
    prepare_ignore_set_from_toml,
)
from codedoctor.config import Config
from codedoctor.engineer.main import create_graph, run_graph


engineer_router = APIRouter()


@engineer_router.post("/api/engineer", response_class=EventSourceResponse)
async def post_engineer(req: EngineerRequest) -> AsyncIterable[ServerSentEvent]:
    root_dir = req.root_dir
    user_prompt = req.user_prompt

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

    graph = create_graph(cfg)
    graph_task = create_task(to_thread(run_graph, graph, user_prompt, cfg))

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
