> # NOTE: This is currently WIP 
  
# CodeDoctor  
CodeDoctor is a CLI tool that helps with testing your code. The Engineer helps create tests, and if something is wrong, the Doctor can help you fix them.
Currently only supports gemini models.  
Expect a couple of bugs.  
# Requirements
#### 1. uv
#### 2. A Gemini api key
# Usage
1. Clone this repository.
2. Run ```uv sync```.
3. Create a .env file with ```GOOGLE_API_KEY=<YOUR API KEY>```.
4. Run ```uv run doctor``` with arguments to fix your failing tests.
5. Run ```uv run engineer``` with arguments to create new tests.
# Options
```
usage: CodeDoctor [-h] [-s dir] [-t dir] [-sm model] [-wm model] [-r retries] [-ig list] [-id] root_dir prompt

positional arguments:
  root_dir              The root directory of the project
  prompt                Prompt for the doctor

options:
  -h, --help            show this help message and exit
  -s, --search-dir dir  The directory relative to the root directory where the source code lives. If the path is absolute, the absolute path is set. (DEFAULT: root_dir /
                        src)
  -t, --test-dir dir    The directory relative to the root directory where tests are stored. If the path is absolute, the absolute path is set. (DEFAULT: root_dir / tests)
  -sm, --strong-model model
                        The model to use for tasks like fixing the code and creating tests. (CURRENTLY GEMINI API MODELS ONLY). (DEFAULT: gemini-3.1-flash-lite)
  -wm, --weak-model model
                        The model to use for detecting failures in tests. (CURRENTLY GEMINI API MODELS ONLY). (DEFAULT: gemma-4-31b-it)
  -r, --max-retries retries
                        Maximum number of times the tests must fail to quit. (DEFAULT: 10)
  -ig, --ignore list    A string of file/folder names that will be excluded from being readable & writable, separated by commas. (DEFAULT: __pycache__, uv.lock)
  -id, --include-dot    Include files/folders starting with '.'
```
