from asyncio import Queue, create_task, to_thread, wait_for
from collections.abc import AsyncIterable
from pathlib import Path
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent
from codedoctor.api.schemas import DoctorRequest
from codedoctor.cli import (
    get_toml_data,
    prepare_exclude_dot_from_toml,
    prepare_ignore_set_from_toml,
)
from codedoctor.config import Config
from codedoctor.doctor.main import (
    create_graph,
    prepare_graph_input,
    run_graph,
    should_run_graph,
)


doctor_router = APIRouter()


@doctor_router.post("/api/doctor", response_class=EventSourceResponse)
async def post_doctor(req: DoctorRequest) -> AsyncIterable[ServerSentEvent]:
    root_dir = req.root_dir
    user_prompt = req.user_prompt or "Fix the test errors."

    path_to_toml = Path(root_dir) / "pyproject.toml"
    toml_data = get_toml_data(path_to_toml)
    ignore_set = prepare_ignore_set_from_toml(toml_data)
    exclude_dot = prepare_exclude_dot_from_toml(toml_data)

    search_dir = req.search_dir or toml_data.get("search_dir")
    test_dir = req.test_dir or toml_data.get("test_dir")
    strong_model = req.strong_model or toml_data.get("strong_model")
    weak_model = req.weak_model or toml_data.get("weak_model")
    max_retries = req.max_retries or toml_data.get("max_retries")

    if req.ignore:
        if isinstance(req.ignore, str):
            ignore_set.update(
                item.strip() for item in req.ignore.split(",") if item.strip()
            )
        elif isinstance(req.ignore, list):
            ignore_set.update(str(item).strip() for item in req.ignore)

    if req.include_dot is not None:
        exclude_dot = not req.include_dot

    cfg = Config(
        root_dir,
        search_dir,
        test_dir,
        strong_model,
        weak_model,
        max_retries,
        ignore_set,
        exclude_dot,
    )

    should_continue, pre_test_result = should_run_graph(cfg)
    if not should_continue:
        yield ServerSentEvent(data="All tests passing. Exiting.", event="done")
        return

    q = Queue()

    def callback(message: str):
        q.put_nowait(message)

    cfg.subscribe(callback)

    graph = create_graph(cfg)
    graph_inputs = prepare_graph_input(pre_test_result, user_prompt, cfg)
    graph_task = create_task(to_thread(run_graph, graph, graph_inputs, cfg))

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
