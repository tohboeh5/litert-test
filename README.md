# LiteRT-Test

This project provides scripts to manage assets for LiteRT-Test, starting with downloading:
1.  A Hugging Face model repository.
2.  A pre-compiled binary file.

## Prerequisites

Before running the script, ensure you have the following installed:

*   **Python 3.7+**: The script is written in Python. You can download it from python.org.
*   **Git**: Required for cloning and updating the Hugging Face model repository. You can download it from git-scm.com.
*   **requests library**: The script uses the `requests` library to download the binary. If you don't have it, you can install it via pip:
    ```bash
    pip install requests
    ```

## Directory Structure

The project has the following basic structure:

```
litert-test/
├── download_assets.py  # Main script to run
├── src/                  # Source code directory
│   ├── __init__.py
│   └── litert_test/
│       ├── __init__.py
│       └── asset_downloader.py # Core download functions
├── model/                # Directory where the Hugging Face model will be cloned (created by the script)
└── binary/               # Directory where the binary will be downloaded (created by the script)
```

## How to Use

1.  **Navigate to the project directory**:
    Open your terminal or command prompt and change to the directory where `download_assets.py` is located.
    ```bash
    cd path/to/litert-test
    ```

2.  **Run the script**:
    Execute the `download_assets.py` script using Python.
    ```bash
    python download_assets.py
    ```

3.  **Follow on-screen prompts**:
    *   **Model Download**:
        *   If the model directory already exists and is a Git repository, you'll be asked if you want to `update (git pull)`, `skip`, or `re-clone` (delete and clone fresh).
        *   If the model directory exists but isn't a Git repository, you'll be asked to `delete and clone` or `skip`.
        *   Otherwise, it will clone the model repository.
    *   **Binary Download**:
        *   If the binary file already exists, you'll be asked if you want to `re-download` it.
        *   Otherwise, it will download the binary.

## Output

After the script runs successfully:
*   The Hugging Face model will be located in the `model/gemma-3n-E4B-it-litert-lm-preview/` directory (or the name specified in the script).
*   The binary file will be located in the `binary/litert_lm_main.macos_arm64` file (or the name specified in the script) and will be made executable.

The script will print the final locations of the downloaded assets.