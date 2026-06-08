from langchain.tools import ToolRuntime, tool

from codedoctor.config import Config
from codedoctor.utils import list_files, read_file, write_to_file


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
    try:
        test_dir = cfg.test_dir.relative_to(cfg.root_dir)
        name = src_path.replace("/", "_")
        name = f"test_{name}"
        path = test_dir / name
        write_to_file(path, code, cfg)
        return f"Successfully created test file at '{path}' to test '{src_path}'."
    except Exception as e:
        return f"Error: {str(e)}"


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
    try:
        contents = read_file(path, cfg)
        return contents
    except FileNotFoundError:
        return f"File not found at {path}. Make sure the path is correct."
    except Exception as e:
        return f"Error: {str(e)}"


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
    try:
        contents = read_file(path, cfg)

        occurences = contents.count(search_block)
        if occurences == 0:
            return f"Error: search block was not found in {path}. Make sure the indentation and spacing is correct"

        new_contents = contents.replace(search_block, replace_block)

        write_to_file(path, new_contents, cfg)
        return f"Successfully updated {path}"

    except FileNotFoundError:
        return f"Error: File {path} not found. Make sure the name is right."

    except Exception as e:
        return f"Error while editing: {str(e)}"
