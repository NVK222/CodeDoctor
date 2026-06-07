from pathlib import Path
import subprocess
from codedoctor.config import Config


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


def list_files(
    dir: Path, ignore: set[str] | None, exclude_dot: bool = True
) -> list[str]:
    files = []

    # TODO : For large directories this may be slow. May need to replace with os cmds
    for file in dir.rglob("*"):
        # Folders / files starting with . are excluded automatically
        if exclude_dot and str(file.relative_to(dir)).startswith("."):
            continue

        # Folders / files in ignore are excluded
        if not file.is_file() or (
            ignore is not None
            and any(ignore_file in str(file) for ignore_file in ignore)
        ):
            continue

        # Retun path relative to specified directory
        files.append(str(file.relative_to(dir)))

    return files
