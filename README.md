# LiteRT-Test

This project provides a script to manage assets for LiteRT-LM, which includes:

1. A Hugging Face model repository.
2. A pre-compiled binary file.

The script can then use these assets to run the LiteRT-LM model.

## Prerequisites

Before running the script, ensure you have the following installed:

* **Python 3.7+**: The script is written in Python. You can download it from python.org.
* **Git**: Required for cloning and updating the Hugging Face model repository. You can download it from git-scm.com.
* **requests library**: The script uses the `requests` library to download the binary. If you don't have it, you can install it via pip:

```bash
pip install requests
```

## Folder Structure

litert-test/
├── download_and_run_litert_model.py  # Main script to download assets and run the LiteRT-LM model
├── src/                              # Source code for helper modules
│   ├── __init__.py                   # Makes 'src' a Python package
│   └── litert_test/
│       ├── __init__.py               # Makes 'litert_test' a Python sub-package
│       ├── asset_downloader.py     # Contains functions for downloading model and binary assets
│       └── model_runner.py         # Contains functions for executing the LiteRT-LM model
├── model/                            # Default directory for the downloaded Hugging Face model repository.
│                                     # Example: model/gemma-3n-E4B-it-litert-lm-preview/
│                                     # (This directory is created by the script if it doesn't exist
│                                     # and downloads are not skipped).
└── binary/                           # Default directory for the downloaded LiteRT-LM binary executable.
                                      # Example: binary/litert_lm_main.macos_arm64
                                      # (This directory and file are created by the script if they don't
                                      # exist and downloads are not skipped).


## How to Use

1.  **Navigate to the project directory**:

Open your terminal or command prompt and change to the root directory of the `litert-test` project.
```bash
cd path/to/litert-test
```

2.  **Run the script**:
Execute the `download_and_run_litert_model.py` script using Python.
* **Basic usage (downloads assets if needed and runs with a default prompt):**
    ```bash
    python download_and_run_litert_model.py
    ```

3.  **Follow on-screen prompts (if any during download)**:
* **Model Download**: By default, the script attempts to download the model from Hugging Face (`google/gemma-3n-E4B-it-litert-lm-preview`) into the `model/` directory.
    * If the model directory (e.g., `model/gemma-3n-E4B-it-litert-lm-preview/`) already exists and is a Git repository, you'll be asked if you want to `update (git pull)`, `skip`, or `re-clone` (delete and clone fresh).
    * If the model directory exists but isn't a Git repository, you'll be asked to `delete and clone` or `skip`.
* **Binary Download**: By default, the script attempts to download the LiteRT-LM binary (e.g., `litert_lm_main.macos_arm64`) into the `binary/` directory.
    * If the binary file already exists, you'll be asked if you want to `re-download` it.

4.  **Command-Line Arguments for More Control**:
The script offers various arguments to customize its behavior. Use `python download_and_run_litert_model.py --help` for a full list of options.

*  * **Model Download**:

* `--skip_download`: Skip the asset download process entirely. The script will then expect assets to be at their default locations or specified via `--model_path` and `--binary_path`.
* `--model_path <path>`: Specify a path to a `.litertlm` model file or a directory containing one. If a directory is given, the script will search for a unique `.litertlm` file. Using this option bypasses the default model download logic for the `model/` directory.
* `--binary_path <path>`: Specify a path to the `litert_lm_main` executable. Using this option bypasses the default binary download logic for the `binary/` directory.
* `--prompt "<your_prompt>"`: The input prompt for the model (e.g., `"What is the capital of France?"`). Default: `"日本の首都はどこですか？"`.
* `--backend <cpu|gpu>`: Specify the execution backend. Default: `cpu`.
* `--benchmark`: Run the model in benchmark mode.
* `--show_stderr`: Always show stderr output from the model execution, even if stdout is present.

## Output

After the script runs successfully:
* **Assets**:
* The Hugging Face model repository (default: `google/gemma-3n-E4B-it-litert-lm-preview`) will be in the `model/gemma-3n-E4B-it-litert-lm-preview/` directory (unless `--model_path` directs elsewhere or download is skipped).
* The script will automatically look for a `*.litertlm` file within the model directory (e.g., `model/gemma-3n-E4B-it-litert-lm-preview/gemma-3n-E4B-it-litert-lm-preview.litertlm`). If multiple or no `.litertlm` files are found in the target model directory, the script will error and may require you to use `--model_path` to specify the exact file.
* The binary file (default: `litert_lm_main.macos_arm64`) will be in the `binary/litert_lm_main.macos_arm64` file (unless `--binary_path` directs elsewhere or download is skipped) and will be made executable by the script.
* **Execution**:
* The script will print progress information during download and execution.
* The model's response (stdout) and any diagnostic messages (stderr) from the LiteRT-LM binary will be displayed.
* Final paths used for the model and binary are summarized at the end.

## Troubleshooting
* **Module Not Found Error**: If you encounter an error like `エラー: 必要なモジュール (...) が見つかりません。` (Error: Required module (...) not found.), ensure you are running the script from the project's root directory (`litert-test/`). The script attempts to import modules from the `src` directory.
* **Git Not Found**: If the model download fails with a "git command not found" error, ensure Git is installed and accessible in your system's PATH.
* **Binary Execution Permissions**: The script attempts to make the downloaded binary executable (`chmod +x`). If this fails on your system, you might need to grant execute permissions manually (e.g., `chmod +x binary/litert_lm_main.macos_arm64`).