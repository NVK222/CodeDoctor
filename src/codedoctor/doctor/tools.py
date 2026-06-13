from langchain.tools import ToolRuntime, tool
from codedoctor.config import Config
from codedoctor.utils import list_files, read_file, write_to_file


@tool
def list_all_files(runtime: ToolRuntime) -> list[str]:
    """
    List all files in the project src.
    Returns:
        All the files in the project src.
    """
    cfg: Config = runtime.state.get("cfg")
    return list_files(cfg.search_dir, cfg)


@tool
def open_file(path: str, runtime: ToolRuntime) -> str:
    """
    Opens file at path and returns the contents as string.
    Args:
        path: A string path relative to the project src. It must be one of the paths returned by list_all_files
    Returns:
        Contents of the file as string if found, else an error message.
    """

    cfg: Config = runtime.state.get("cfg")
    return read_file(path, cfg)


@tool
def edit_file(
    path: str, search_block: str, replace_block: str, runtime: ToolRuntime
) -> str:
    """
    Safely replaces a specific block of code inside a file.
    Args:
        path: The relative path to the target file from project src. It must be one of the paths returned by list_all_files
        search_block: The exact, existing code block to find (include indentation).
        replace_block: The new code block to replace the search_block with.
    Returns:
        A success message or a detailed error message if the block wasn't found.
    """
    cfg: Config = runtime.state.get("cfg")
    contents = read_file(path, cfg)

    occurences = contents.count(search_block)
    if occurences == 0:
        raise ValueError(
            f"Error: search block was not found in {path}. Make sure the indentation and spacing is correct"
        )

    new_contents = contents.replace(search_block, replace_block)

    write_to_file(path, new_contents, cfg)
    return f"Successfully updated {path}"
