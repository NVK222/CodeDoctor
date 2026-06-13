import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser("CodeDoctor")

    parser.add_argument(
        "root_dir",
        help="The root directory of the project",
        type=lambda p: Path(p).resolve(),
    )
    parser.add_argument("prompt", help="Prompt for the doctor")
    parser.add_argument(
        "-s",
        "--search-dir",
        help="The directory relative to the root directory where the source code lives. If the path is absolute, the absolute path is set. (DEFAULT: root_dir / src)",
        type=str,
        default="src",
        metavar="dir",
    )
    parser.add_argument(
        "-t",
        "--test-dir",
        help="The directory relative to the root directory where tests are stored. If the path is absolute, the absolute path is set. (DEFAULT: root_dir / tests)",
        type=str,
        default="tests",
        metavar="dir",
    )

    parser.add_argument(
        "-sm",
        "--strong-model",
        help="The model to use for tasks like fixing the code and creating tests. (CURRENTLY GEMINI API MODELS ONLY). (DEFAULT: gemini-3.1-flash-lite)",
        default="gemini-3.1-flash-lite",
        metavar="model",
    )

    parser.add_argument(
        "-wm",
        "--weak-model",
        help="The model to use for detecting failures in tests. (CURRENTLY GEMINI API MODELS ONLY). (DEFAULT: gemma-4-31b-it)",
        default="gemma-4-31b-it",
        metavar="model",
    )

    parser.add_argument(
        "-r",
        "--max-retries",
        help="Maximum number of times the tests must fail to quit. (DEFAULT: 10)",
        type=int,
        default=10,
        metavar="retries",
    )

    parser.add_argument(
        "-ig",
        "--ignore",
        help="A string of file/folder names that will be excluded from being readable & writable, separated by commas. (DEFAULT: __pycache__, uv.lock)",
        type=lambda s: {item.strip() for item in s.split(",")},
        default={"__pycache__", "uv.lock"},
        metavar="list",
    )

    parser.add_argument(
        "-id",
        "--include-dot",
        help="Include files/folders starting with '.'",
        action="store_true",
    )

    args = parser.parse_args()

    return args
