from asyncio import create_subprocess_exec
import asyncio
from pathlib import Path
from datetime import datetime
from codedoctor.config import Config


success_exit_codes = ["EXIT_CODE:0", "EXIT_CODE:5"]


def is_test_successful(
    test_result: str, success_exit_codes: list[str] = success_exit_codes
) -> bool:
    if any(exit_code in test_result for exit_code in success_exit_codes):
        return True
    return False


async def run_tests(test_dir: Path) -> str:
    process = await create_subprocess_exec(
        "pytest",
        "-v",
        "--no-header",
        str(test_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await process.communicate()
    stdout = out.decode("utf-8", errors="ignore") if out else ""
    stderr = err.decode("utf-8", errors="ignore") if err else ""
    output = f"STDOUT:\n{stdout}\nSTDERR:\n:{stderr}\nEXIT_CODE:{process.returncode}"
    return output


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
