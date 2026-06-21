from pathlib import Path
import toml
from fastapi import APIRouter, HTTPException

from codedoctor.api.schemas import LoadContextSchema, SaveConfigRequest
from codedoctor.cli import (
    get_toml_data,
    prepare_exclude_dot_from_toml,
    prepare_ignore_set_from_toml,
)
from codedoctor.config import Config


context_router = APIRouter()


@context_router.get("/api/context")
def get_context(root_dir: str) -> LoadContextSchema:
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

    return LoadContextSchema(
        search_dir=str(cfg.search_dir),
        test_dir=str(cfg.test_dir),
        strong_model=cfg.strong_model_name,
        weak_model=cfg.weak_model_name,
        max_retries=cfg.max_retries,
        ignore=cfg.ignore_list,
        include_dot=not cfg.exclude_dot,
    )


@context_router.post("/api/context")
def save_config(payload: SaveConfigRequest):
    root_dir = Path(payload.root_dir)
    toml_path = root_dir / "pyproject.toml"

    if not toml_path.exists():
        raise HTTPException(404, f"pyproject.toml not found at {toml_path}")

    try:
        with open(toml_path, "r") as fp:
            full_toml = toml.load(fp)

        if "tool" not in full_toml:
            full_toml["tool"] = {}

        full_toml["tool"]["codedoctor"] = payload.config.model_dump()

        with open(toml_path, "w") as fp:
            toml.dump(full_toml, fp)

        return {
            "status": "success",
            "message": "Config successfully saved to pyproject.toml",
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to write config: {str(e)}")
