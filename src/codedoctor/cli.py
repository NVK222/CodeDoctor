import argparse
from pathlib import Path
import tomllib
import urllib.parse
import webbrowser

from codedoctor.config import Config


def parse_args(is_prompt_optional: str):
    parser = argparse.ArgumentParser("CodeDoctor")

    parser.add_argument(
        "root_dir",
        help="The root directory of the project",
        type=lambda p: Path(p).resolve(),
    )
    if is_prompt_optional:
        parser.add_argument(
            "-p", "--prompt", help="Prompt", type=str, default=None, metavar="prompt"
        )
    else:
        parser.add_argument("prompt", help="Prompt", type=str)
    parser.add_argument(
        "-s",
        "--search-dir",
        help="The directory relative to the root directory where the source code lives. If the path is absolute, the absolute path is set. (DEFAULT: root_dir / src)",
        type=str,
        default=None,
        metavar="dir",
    )
    parser.add_argument(
        "-t",
        "--test-dir",
        help="The directory relative to the root directory where tests are stored. If the path is absolute, the absolute path is set. (DEFAULT: root_dir / tests)",
        type=str,
        default=None,
        metavar="dir",
    )

    parser.add_argument(
        "-sm",
        "--strong-model",
        help="The model to use for tasks like fixing the code and creating tests. (CURRENTLY GEMINI API MODELS ONLY). (DEFAULT: gemini-3.1-flash-lite)",
        default=None,
        metavar="model",
    )

    parser.add_argument(
        "-wm",
        "--weak-model",
        help="The model to use for detecting failures in tests. (CURRENTLY GEMINI API MODELS ONLY). (DEFAULT: gemma-4-31b-it)",
        default=None,
        metavar="model",
    )

    parser.add_argument(
        "-r",
        "--max-retries",
        help="Maximum number of times the tests must fail to quit. (DEFAULT: 10)",
        type=int,
        default=None,
        metavar="retries",
    )

    parser.add_argument(
        "-ig",
        "--ignore",
        help="A string of file/folder names that will be excluded from being readable & writable, separated by commas. These will overwrite the dafaults and add to the ones declared in pyproject.toml (DEFAULT: __pycache__, uv.lock)",
        type=lambda s: {item.strip() for item in s.split(",")},
        default=None,
        metavar="list",
    )

    parser.add_argument(
        "-id",
        "--include-dot",
        help="Include files/folders starting with '.'",
        action="store_const",
        const=True,
        default=None,
    )

    args = parser.parse_args()

    return args


def get_toml_data(path_to_toml: Path) -> dict[str]:
    if path_to_toml.exists():
        try:
            with open(path_to_toml, "rb") as f:
                data = tomllib.load(f)
                toml_data = data.get("tool", {}).get("codedoctor", {})
        except Exception:
            toml_data = {}
    else:
        toml_data = {}
    return toml_data


def prepare_ignore_set_from_toml(toml_data: dict[str, str | list]) -> set[str]:
    toml_ignore = toml_data.get("ignore")
    ignore_set = set()
    if isinstance(toml_ignore, str):
        ignore_set.update(
            item.strip() for item in toml_ignore.split(",") if item.strip()
        )
    elif isinstance(toml_ignore, list):
        ignore_set.update(str(item).strip() for item in toml_ignore)
    return ignore_set


def prepare_exclude_dot_from_toml(toml_data: dict[str, bool]) -> bool | None:
    exclude_dot = None
    if toml_data.get("include_dot") is not None:
        exclude_dot = not toml_data.get("include_dot")
    return exclude_dot


def initialize_config(is_prompt_optional: str = True) -> tuple[Config, str]:
    args = parse_args(is_prompt_optional)

    path_to_toml = Path(args.root_dir) / "pyproject.toml"
    toml_data = get_toml_data(path_to_toml)

    ignore_set = prepare_ignore_set_from_toml(toml_data)
    if args.ignore is not None:
        ignore_set.update(args.ignore)

    exclude_dot = prepare_exclude_dot_from_toml(toml_data)
    if args.include_dot is not None:
        exclude_dot = not args.include_dot

    cfg = Config(
        args.root_dir,
        args.search_dir or toml_data.get("search_dir"),
        args.test_dir or toml_data.get("test_dir"),
        args.strong_model or toml_data.get("strong_model"),
        args.weak_model or toml_data.get("weak_model"),
        args.max_retries or toml_data.get("max_retries"),
        ignore_set,
        exclude_dot,
    )

    return (cfg, args.prompt)


def run_gui():
    parser = argparse.ArgumentParser("CodeDoctor")

    parser.add_argument(
        "root_dir",
        help="The root directory of the project",
        type=lambda p: Path(p).resolve(),
    )

    args = parser.parse_args()
    path = str(args.root_dir)

    url = f"http://localhost:5173/?root_dir={urllib.parse.quote(path, safe='')}"
    webbrowser.open(url)
