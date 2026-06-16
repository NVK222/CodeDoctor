from pathlib import Path
import subprocess
from datetime import datetime
from codedoctor.config import Config


def run_tests(test_dir: Path) -> str:
    result = subprocess.run(
        ["pytest", "-v", "--no-header", str(test_dir)], capture_output=True, text=True
    )
    output = f"STDOUT:\n{result.stdout}\nSTDERR:\n:{result.stderr}\nEXIT_CODE:{result.returncode}"
    if result.returncode == 0:
        return output
    else:
        return f"Tests failed. Here is the output\n{output}"


def print_to_terminal(message: str) -> None:
    print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]\t{message}")


def read_file(path: str, cfg: Config) -> str:
    p = Path(path)
    file_path = p if p.is_absolute() else cfg.root_dir / p
    try:
        with open(file_path, "r") as fp:
            return fp.read()
    except FileNotFoundError:
        raise
    except Exception:
        raise


def write_to_file(path: str, content: str, cfg: Config) -> None:
    p = Path(path)
    file_path = p if p.is_absolute() else cfg.root_dir / p
    try:
        with open(file_path, "w") as fp:
            fp.write(content)
    except FileNotFoundError:
        raise
    except Exception:
        raise


def list_files(dir: Path, cfg: Config) -> list[str]:
    files = []

    # TODO : For large directories this may be slow. May need to replace with os cmds
    for file in dir.rglob("*"):
        # Folders / files starting with . are excluded automatically
        if cfg.exclude_dot and str(file.relative_to(dir)).startswith("."):
            continue

        # Folders / files in ignore are excluded
        if not file.is_file() or (
            cfg.ignore_list is not None
            and any(ignore_file in str(file) for ignore_file in cfg.ignore_list)
        ):
            continue

        if file.is_relative_to(cfg.root_dir):
            files.append(str(file.relative_to(cfg.root_dir)))
        else:
            files.append(str(file.resolve()))

    return files
