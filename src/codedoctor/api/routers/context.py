from pathlib import Path

from fastapi import APIRouter

from codedoctor.api.schemas import ContextSchema
from codedoctor.cli import (
    get_toml_data,
    prepare_exclude_dot_from_toml,
    prepare_ignore_set_from_toml,
)
from codedoctor.config import Config


context_router = APIRouter()


@context_router.get("/api/context")
def get_context(root_dir: str) -> ContextSchema:
    path_to_toml = Path(root_dir) / "pyproject.toml"
    toml_data = get_toml_data(path_to_toml)
    ignore_set = prepare_ignore_set_from_toml(toml_data)
    exclude_dot = prepare_exclude_dot_from_toml(toml_data)

    search_dir = toml_data.get("search_dir")
    test_dir = toml_data.get("test_dir")
    strong_model = toml_data.get("strong_model")
    weak_model = toml_data.get("weak_model")
    max_retries = toml_data.get("max_retries")

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

    return ContextSchema(
        search_dir=str(cfg.search_dir),
        test_dir=str(cfg.test_dir),
        strong_model=cfg.strong_model_name,
        weak_model=cfg.weak_model_name,
        max_retries=cfg.max_retries,
        ignore=cfg.ignore_list,
        include_dot=not cfg.exclude_dot,
    )
