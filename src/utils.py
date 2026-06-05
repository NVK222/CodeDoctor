from pathlib import Path
import subprocess


def get_project_root() -> Path:
    """
    Returns the project root.
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return current.parent


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
