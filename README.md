> # NOTE: This is currently WIP 
  
# CodeDoctor  
CodeDoctor is a CLI tool that automatically runs tests in your project and fixes them automatically if they fail.  
Currently only supports gemini models.  
Expect a couple of bugs.  
# Requirements
### 1. uv
### 2. A Gemini api key
# Usage
1. Clone this repository.
2. Run ```uv sync```.
3. Create a .env file with ```GOOGLE_API_KEY=<YOUR API KEY>```.
4. Run ```uv run main``` with arguments.
# Options
```
usage: CodeDoctor [-h] [-s SEARCH_DIR] [-t TEST_DIR] [-m MODEL] [-r MAX_RETRIES] [-ig IGNORE] [-id] root_dir prompt

positional arguments:
  root_dir              The root directory of the project
  prompt                Prompt for the doctor

options:
  -h, --help            show this help message and exit
  -s, --search-dir SEARCH_DIR
                        The directory relative to the root directory where the files will be searched and opened.
  -t, --test-dir TEST_DIR
                        The directory relative to the root directory where tests are stored.
  -m, --model MODEL     The model to be used. (CURRENTLY GEMINI API MODELS ONLY)
  -r, --max-retries MAX_RETRIES
                        Maximum number of times the tests must fail to quit
  -ig, --ignore IGNORE  A set of file/folder names that will be excluded from being opened and searched separated by commas.
  -id, --include-dot    Include files/folders starting with '.'
```
