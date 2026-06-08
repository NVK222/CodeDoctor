import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from codedoctor.utils import run_tests, read_file, write_to_file, list_files
from codedoctor.config import Config

@patch("subprocess.run")
def test_run_tests_success(mock_run):
    mock_run.return_value = MagicMock(stdout="passed", stderr="", returncode=0)
    result = run_tests(Path("tests"))
    assert "All tests passed successfully" in result
    assert "passed" in result
    mock_run.assert_called_once_with(["pytest", "-v", "tests"], capture_output=True, text=True)

@patch("subprocess.run")
def test_run_tests_failure(mock_run):
    mock_run.return_value = MagicMock(stdout="failed", stderr="error", returncode=1)
    result = run_tests(Path("tests"))
    assert "Tests failed" in result
    assert "failed" in result
    assert "error" in result

def test_read_file(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    f = d / "hello.txt"
    f.write_text("content")
    
    cfg = MagicMock(spec=Config)
    cfg.root_dir = tmp_path
    
    assert read_file("subdir/hello.txt", cfg) == "content"

def test_read_file_not_found():
    cfg = MagicMock(spec=Config)
    cfg.root_dir = Path("/tmp/nonexistent")
    with pytest.raises(FileNotFoundError):
        read_file("file.txt", cfg)

def test_write_to_file(tmp_path):
    cfg = MagicMock(spec=Config)
    cfg.root_dir = tmp_path
    
    write_to_file("newfile.txt", "some content", cfg)
    
    assert (tmp_path / "newfile.txt").read_text() == "some content"

def test_list_files(tmp_path):
    (tmp_path / "a.py").touch()
    (tmp_path / "b.txt").touch()
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/config").touch()
    
    cfg = Config()
    cfg.root_dir = tmp_path
    cfg.exclude_dot = True
    cfg.ignore_list = None
    
    files = list_files(tmp_path, cfg)
    assert "a.py" in files
    assert "b.txt" in files
    assert ".git/config" not in files
