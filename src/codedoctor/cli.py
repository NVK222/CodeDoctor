import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser("CodeDoctor")

    parser.add_argument("root_dir", help="The root directory of the project", type=Path)
    parser.add_argument("prompt", help="Prompt for the doctor")
    parser.add_argument(
        "-s",
        "--search-dir",
        help="The directory relative to the root directory where the files will be searched and opened.",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "-t",
        "--test-dir",
        help="The directory relative to the root directory where tests are stored.",
        type=Path,
        default=None,
    )

    parser.add_argument(
        "-m",
        "--model",
        help="The model to be used. (CURRENTLY GEMINI API MODELS ONLY)",
        default="gemini-3.1-flash-lite",
    )

    parser.add_argument(
        "-r",
        "--max-retries",
        help="Maximum number of times the tests must fail to quit",
        type=int,
        default=10,
    )

    parser.add_argument(
        "-ig",
        "--ignore",
        help="A set of file/folder names that will be excluded from being opened and searched separated by commas.",
        type=lambda s: {item.strip() for item in s.split(",")},
        default={"__pycache__", "uv.lock"},
    )

    parser.add_argument(
        "-id",
        "--include-dot",
        help="Include files/folders starting with '.'",
        action="store_true",
    )

    args = parser.parse_args()

    args.root_dir = Path(args.root_dir).absolute()

    if args.search_dir is None:
        args.search_dir = args.root_dir

    if args.test_dir is None:
        args.test_dir = args.root_dir / "tests"

    return args
