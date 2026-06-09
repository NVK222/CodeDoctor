from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Config:
    def __init__(
        self,
        root_dir: Path,
        search_dir: str | None = None,
        test_dir: str | None = None,
        model_name: str | None = None,
        max_retries: int | None = None,
        ignore_list: set[str] = None,
        exclude_dot: bool | None = None,
    ) -> None:
        """
        Initializes the config.
        Args:
            root_dir: The project root.
            search_dir: A path relative to project_root, where the actual source code lives. Default: project_root / src
            test_dir: A path relative to project root, where tests are stored. Default: project_root / tests
            model_name: The model to use. (CURRENTLY ONLY GEMINI API MODELS). Default: 'gemini-3.1-flash-lite'
            max_retries: Maximum number of times the tests must fail to quit. Default: 10
            ignore_list: A set of file/folder names that will be excluded from being opened and searched. Default: {'__pycache', '.lock'}
            exclude_dot: A boolean that decides whether to exclude files/folders starting with '.' Default: True
        """
        self.model_name = "gemini-3.1-flash-lite"
        self.max_retries = 10
        self.ignore_list = {"__pycache__", ".lock"}
        self.exclude_dot = True
        self.root_dir = root_dir

        if model_name:
            self.model_name = model_name
        if max_retries:
            self.max_retries = max_retries
        if ignore_list:
            self.ignore_list = ignore_list
        if exclude_dot is not None:
            self.exclude_dot = exclude_dot
        if search_dir:
            p = Path(search_dir)
            if p.is_absolute():
                self.search_dir = p.resolve()
            else:
                self.search_dir = (self.root_dir / p).resolve()
        if test_dir:
            p = Path(test_dir)
            if p.is_absolute():
                self.test_dir = p.resolve()
            else:
                self.test_dir = (self.root_dir / p).resolve()

    @property
    def root_dir(self) -> Path:
        return self._root_dir.resolve()

    @root_dir.setter
    def root_dir(self, value: str | Path) -> None:
        self._root_dir = Path(value).resolve()
        self.search_dir = (self._root_dir / "src").resolve()
        self.test_dir = (self._root_dir / "tests").resolve()
