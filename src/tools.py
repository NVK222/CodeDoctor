from langchain.tools import ToolRuntime, tool
from config import Config
from utils import read_file, write_to_file


@tool
def list_files(runtime: ToolRuntime) -> list[str]:
    """
    List all files in the project root.
    Returns:
        All the files in the project root.
    """
    files = []
    cfg: Config = runtime.state.get("cfg")

    # TODO : For large directories this may be slow. May need to replace with os cmds
    for file in cfg.search_dir.rglob("*"):
        # Folders / files starting with . are excluded automatically
        if str(file.relative_to(cfg.search_dir)).startswith("."):
            continue

        # Folders / files in ignore are excluded
        if not file.is_file() or any(
            ignore_file in str(file) for ignore_file in cfg.ignore_list
        ):
            continue

        # Retun path relative to root
        files.append(str(file.relative_to(cfg.root_dir)))

    return files


@tool
def open_file(path: str, runtime: ToolRuntime) -> str:
    """
    Opens file at path and returns the contents as string.
    Args:
        path: A string path relative to the project root. It must be one of the paths returned by list_files
    Returns:
        Contents of the file as string if found, else an error message.
    """

    cfg: Config = runtime.state.get("cfg")
    try:
        contents = read_file(path, cfg)
        return contents

    except FileNotFoundError:
        return f"Error: File at path {path} was not found. Make sure the path is right."


@tool
def edit_file(
    path: str, search_block: str, replace_block: str, runtime: ToolRuntime
) -> str:
    """
    Safely replaces a specific block of code inside a file.
            max_retries: Maximum number of times the tests must fail to quit. Default: 10
    Args:
        path: The relative path to the target file from project root. It must be one of the paths returned by list_files
        search_block: The exact, existing code block to find (include indentation).
        replace_block: The new code block to replace the search_block with.
    Returns:
        A success message or a detailed error message if the block wasn't found.
    """
    cfg: Config = runtime.state.get("cfg")
    try:
        contents = read_file(path, cfg)

        occurences = contents.count(search_block)
        if occurences == 0:
            return f"Error: search block was not found in {path}. Make sure the indentation and spacing is correct"

        new_contents = contents.replace(search_block, replace_block)

        write_to_file(path, new_contents, cfg)
        return f"Successfully updated {path}"

    except FileNotFoundError:
        return f"Error: File at path {path} not found. Make sure the path is right."

    except Exception as e:
        return f"Error while editing: {str(e)}"
