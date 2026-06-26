from langchain.tools import ToolRuntime, tool

from codedoctor.config import Config
from codedoctor.utils import append_to_file, list_files, read_file, write_to_file


@tool
def create_test(src_path: str, code: str, runtime: ToolRuntime) -> str:
    """
    Creates a new test file inside the test directory for a specified source file.

    Args:
        src_path: The exact relative path of the source file to test,
                  exactly as returned by list_src() (e.g., 'src/codedoctor/utils.py').
        code: The complete, raw Python test code block containing the pytest assertions.
    Returns:
        A success confirmation string or a detailed error message.
    """
    cfg: Config = runtime.state.get("cfg")
    name = src_path.lstrip("/").replace("/", "_").replace("\\", "_")
    name = f"test_{name}"
    path = cfg.test_dir / name
    write_to_file(str(path), code, cfg)
    display_path = (
        path.relative_to(cfg.root_dir) if path.is_relative_to(cfg.root_dir) else path
    )
    return f"Successfully created test file at '{display_path}' to test '{src_path}'."


@tool
def list_tests(runtime: ToolRuntime) -> list[str]:
    """
    List all the tests in test directory.
    Returns:
        A list of file paths relative to the tests directory
    """

    cfg: Config = runtime.state.get("cfg")
    return list_files(cfg.test_dir, cfg)


@tool
def list_src(runtime: ToolRuntime) -> list[str]:
    """
    List all the source code files. The tests will be created for these files if they don't already exist.
    Returns:
        A list of file paths relative to the src directory.
    """
    cfg: Config = runtime.state.get("cfg")
    return list_files(cfg.search_dir, cfg)


@tool
def open_src(path: str, runtime: ToolRuntime) -> str:
    """
    Read the entire source code from a file in source directory.
    Args:
        path: A path in source directory. It must be one of the paths returned by list_src
    Returns:
        The entire code in the file as a string or an error message
    """

    cfg: Config = runtime.state.get("cfg")
    contents = read_file(path, cfg)
    return contents


@tool
def edit_test(
    path: str, search_block: str, replace_block: str, runtime: ToolRuntime
) -> str:
    """
    Safely replaces a specific block of code inside a test file.
    Args:
        path: The name of the test file to edit. The name should be one of the names returned by list_tests
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


@tool
def add_test(path: str, code: str, runtime: ToolRuntime):
    """
    Appends a new test function or block of code to the end of an existing test file.
    Use this when you want to add new tests without modifying existing ones.
    Args:
        path: The name of the test file to append to. Must be one of the paths returned by list_tests().
        code: The raw Python code block/test to add to the end of file.
    Returns:
        A success confirmation string or a detailed error message.
    """
    cfg: Config = runtime.state.get("cfg")
    formatted_code = f"\n\n{code}\n"
    append_to_file(path, formatted_code, cfg)
    return f"Successfully appended new test code to end of {path}"
