from pathlib import Path
import subprocess
from config import Config


def run_tests(test_dir: Path) -> str:
    """
    Runs tests on the whole project and returns the terminal output.
    """

    result = subprocess.run(
        ["pytest", "-v", str(test_dir)], capture_output=True, text=True
    )
    output = f"STDOUT:\n{result.stdout}\nSTDERR:\n:{result.stderr}"
    if result.returncode == 0:
        return f"All tests passed successfully\n{output}"
    else:
        return f"Tests failed. Here is the output\n{output}"


def read_file(path: str, cfg: Config) -> str:
    file_path = cfg.root_dir / path
    try:
        with open(file_path, "r") as fp:
            return fp.read()
    except FileNotFoundError:
        raise
    except Exception:
        raise


def write_to_file(path: str, content: str, cfg: Config) -> None:
    file_path = cfg.root_dir / path
    try:
        with open(file_path, "w") as fp:
            fp.write(content)
    except FileNotFoundError:
        raise
    except Exception:
        raise
