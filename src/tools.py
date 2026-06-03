import subprocess

from langchain.tools import tool
from pathlib import Path
from utils import get_project_root
import os
import pytest


@tool
def list_files() -> list[str]:
    """
    List all files in path project_root/src
    Returns:
        All the files in the src directory of project root.
    """
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
    """
    Opens file at path and returns the contents as string.
    Args:
        path: A string path relative to the root of the directory, starting with src/
    Returns:
        Contents of the file as string if found, else an error message.
    """
    file_path = get_project_root() / path
    if not os.path.exists(file_path):
        return f"The file at {path} does not exist."
    with open(file_path, "r") as fp:
        return fp.read()


@tool
def edit_file(path: str, search_block: str, replace_block: str) -> str:
    """
    Safely replaces a specific block of code inside a file.
    Args:
        path: The relative path to the target file from project root.
        search_block: The exact, existing code block to find (include indentation).
        replace_block: The new code block to replace the search_block with.
    Returns:
        A success message or a detailed error message if the block wasn't found.
    """
    try:
        contents: str = open_file.invoke({"path": path})
        occurences = contents.count(search_block)
        if occurences == 0:
            return f"Error: search block was not found in {path}. Make sure the indentation and spacing is correct"
        new_contents = contents.replace(search_block, replace_block)
        with open(get_project_root() / path, "w") as fp:
            fp.write(new_contents)
        return f"Successfully updated {path}"
    except Exception as e:
        return f"Error while editing: {str(e)}"


@tool
def run_tests() -> str:
    """
    Runs tests on the whole project and returns the terminal output.
    """

    test_dir = get_project_root() / "tests"
    result = subprocess.run(
        ["pytest", "-v", str(test_dir)], capture_output=True, text=True
    )
    output = f"STDOUT:\n{result.stdout}\nSTDERR:\n:{result.stderr}"
    if result.returncode == 0:
        return f"All tests passed successfully\n{output}"
    else:
        return f"Tests failed. Here is the output\n{output}"
