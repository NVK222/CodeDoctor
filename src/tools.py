import subprocess
from langchain.tools import tool
from utils import get_project_root
import os


@tool
def list_files() -> list[str]:
    """
    List all files in the project root.
    Returns:
        All the files in the project root.
    """
    search_dir = get_project_root()
    files = []

    # Ignore list
    ignore = {"__pycache__", ".lock"}

    # TODO : For large directories this may be slow. May need to replace with os cmds
    for file in search_dir.rglob("*"):
        # Folders / files starting with . are excluded automatically
        if str(file.relative_to(search_dir)).startswith("."):
            continue

        # Folders / files in ignore are excluded
        if not file.is_file() or any(
            ignore_file in str(file) for ignore_file in ignore
        ):
            continue

        # Retun path relative to root
        files.append(str(file.relative_to(get_project_root())))
    return files


@tool
def open_file(path: str) -> str:
    """
    Opens file at path and returns the contents as string.
    Args:
        path: A string path relative to the project root. It must be one of the paths returned by list_files
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
        path: The relative path to the target file from project root. It must be one of the paths returned by list_files
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
