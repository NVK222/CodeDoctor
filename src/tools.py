from langchain.tools import tool
from pathlib import Path
from utils import get_project_root


@tool
def list_files() -> list[str]:
    """List all files in path project_root/src"""
    search_dir = get_project_root() / "src"
    files = []
    ignore = {"__pycache__"}
    for file in search_dir.rglob("*"):
        if not file.is_file() or any(
            ignore_file in str(file) for ignore_file in ignore
        ):
            continue
        files.append(str(file.relative_to(get_project_root())))
    return files


@tool
def open_file(path: str) -> str:
    """Opens file at src/path and returns its contents"""
    file_path = get_project_root() / path
    with open(file_path, "r") as fp:
        return fp.read()
