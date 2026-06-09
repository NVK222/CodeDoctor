import pytest
from pathlib import Path
from unittest.mock import patch
from codedoctor.cli import parse_args
from codedoctor.config import Config

def test_cli_paths_to_config_resolution():
    root = Path("/tmp/project").resolve()
    
    # Simulate CLI arguments
    test_args = [
        str(root),
        "do something",
        "--search-dir", "my_src",
        "--test-dir", "/tmp/absolute_tests"
    ]
    
    with patch("sys.argv", ["codedoctor"] + test_args):
        args = parse_args()
        
    config = Config(
        root_dir=args.root_dir,
        search_dir=args.search_dir,
        test_dir=args.test_dir
    )
    
    # Assertions
    assert config.root_dir == root
    assert config.search_dir == (root / "my_src").resolve()
    assert config.test_dir == Path("/tmp/absolute_tests").resolve()

def test_cli_default_paths():
    root = Path("/tmp/default_project").resolve()
    
    test_args = [str(root), "prompt"]
    
    with patch("sys.argv", ["codedoctor"] + test_args):
        args = parse_args()
        
    config = Config(
        root_dir=args.root_dir,
        search_dir=args.search_dir,
        test_dir=args.test_dir
    )
    
    assert config.search_dir == (root / "src").resolve()
    assert config.test_dir == (root / "tests").resolve()
