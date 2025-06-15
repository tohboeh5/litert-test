import subprocess
import requests
from pathlib import Path
import shutil
import sys

# --- 設定 ---
MODEL_REPO_URL = "https://huggingface.co/google/gemma-3n-E4B-it-litert-lm-preview"
MODEL_PARENT_DIR = Path("model")  # モデルの親ディレクトリ
MODEL_NAME = MODEL_REPO_URL.split("/")[-1]
MODEL_DEST_PATH = MODEL_PARENT_DIR / MODEL_NAME  # クローンされたリポジトリのフルパス

BINARY_URL = "https://github.com/google-ai-edge/LiteRT-LM/releases/latest/download/litert_lm_main.macos_arm64"
BINARY_PARENT_DIR = Path("binary")  # バイナリの親ディレクトリ
BINARY_FILENAME = BINARY_URL.split("/")[-1]
BINARY_DEST_PATH = BINARY_PARENT_DIR / BINARY_FILENAME  # バイナリファイルのフルパス

# --- ヘルパー関数 ---
def create_dir_if_not_exists(directory_path: Path):
    """ディレクトリが存在しない場合に作成します。"""
    if not directory_path.exists():
        print(f"ディレクトリを作成中: {directory_path}")
        directory_path.mkdir(parents=True, exist_ok=True)

# --- ダウンロード関数 ---
def download_huggingface_model():
    """Hugging Faceモデルリポジトリをダウンロードまたは更新します。"""
    print(f"\n--- Hugging Faceモデルの処理中: {MODEL_NAME} ---")
    create_dir_if_not_exists(MODEL_PARENT_DIR)  # 親の 'model' ディレクトリの存在を確認

    is_git_repo = (MODEL_DEST_PATH / ".git").is_dir()

    if MODEL_DEST_PATH.exists() and is_git_repo:
        print(f"モデルリポジトリは既に存在します: {MODEL_DEST_PATH}")
        choice = input("更新 (git pull) (u), スキップ (s), または再クローン (既存を削除) (r) を選択してください [u/s/r]: ").lower()
        if choice == 'u':
            print(f"{MODEL_DEST_PATH} のモデルリポジトリを更新中...")
            try:
                # --progress を追加し、capture_output を削除してgitの出力を直接表示
                subprocess.run(
                    ["git", "-C", str(MODEL_DEST_PATH), "pull", "--progress"],
                    check=True
                )
                print("モデルリポジトリが正常に更新されました。")
            except subprocess.CalledProcessError as e:
                # e.stderr はキャプチャされないためNoneになる。gitがエラーを直接表示する。
                print(f"モデルリポジトリの更新エラーが発生しました。gitからのメッセージは上記に表示されているはずです。 (コマンド: {' '.join(e.cmd)})")
            except FileNotFoundError:
                print("エラー: gitコマンドが見つかりません。gitがインストールされ、PATHが通っていることを確認してください。")
            return
        elif choice == 's':
            print("モデル処理をスキップします。")
            return
        elif choice == 'r':
            print(f"既存のモデルディレクトリを削除中: {MODEL_DEST_PATH}")
            try:
                shutil.rmtree(MODEL_DEST_PATH)
                print(f"ディレクトリ {MODEL_DEST_PATH} が削除されました。再クローンに進みます。")
            except OSError as e:
                print(f"ディレクトリ {MODEL_DEST_PATH} の削除エラー: {e}。手動で削除して再試行してください。")
                return
        else:
            print("無効な選択です。モデル処理をスキップします。")
            return
    elif MODEL_DEST_PATH.exists() and not is_git_repo:
        print(f"警告: ディレクトリ {MODEL_DEST_PATH} は存在しますが、gitリポジトリではありません。")
        choice = input("削除してクローン (d), またはスキップ (s) を選択してください [d/s]: ").lower()
        if choice == 'd':
            print(f"非gitディレクトリを削除中: {MODEL_DEST_PATH}")
            try:
                shutil.rmtree(MODEL_DEST_PATH)
                print(f"ディレクトリ {MODEL_DEST_PATH} が削除されました。クローンに進みます。")
            except OSError as e:
                print(f"ディレクトリ {MODEL_DEST_PATH} の削除エラー: {e}。手動で削除して再試行してください。")
                return
        else:
            print("既存の非gitディレクトリのため、モデルのクローンをスキップします。")
            return
    
    print(f"{MODEL_REPO_URL} から {MODEL_DEST_PATH} へモデルリポジトリをクローン中...")
    try:
        subprocess.run(
            # --progress を追加し、capture_output を削除してgitの出力を直接表示
            ["git", "clone", "--progress", "--depth", "1", MODEL_REPO_URL, str(MODEL_DEST_PATH)],
            check=True
        )
        print("モデルリポジトリが正常にクローンされました。")
    except subprocess.CalledProcessError as e:
        # e.stderr はキャプチャされないためNoneになる。gitがエラーを直接表示する。
        print(f"モデルリポジトリのクローンエラーが発生しました。gitからのメッセージは上記に表示されているはずです。")
        print(f"実行しようとしたコマンド: {' '.join(e.cmd)}")
        print("ヒント: gitがインストールされ、ネットワークアクセスがあり、ターゲットパスが書き込み可能であることを確認してください。")
    except FileNotFoundError:
        print("エラー: gitコマンドが見つかりません。gitがインストールされ、PATHが通っていることを確認してください。")

def download_binary_file():
    """バイナリファイルをダウンロードまたは再ダウンロードします。"""
    print(f"\n--- バイナリファイルの処理中: {BINARY_FILENAME} ---")
    create_dir_if_not_exists(BINARY_PARENT_DIR)  # 親の 'binary' ディレクトリの存在を確認
    
    if BINARY_DEST_PATH.exists():
        print(f"バイナリファイル {BINARY_DEST_PATH} は既に存在します。")
        if input("再ダウンロードしますか？ (y/n): ").lower() != 'y':
            print("バイナリのダウンロードをスキップします。")
            return
            
    print(f"{BINARY_URL} から {BINARY_DEST_PATH} へバイナリをダウンロード中...")
    try:
        with requests.get(BINARY_URL, stream=True, timeout=60, allow_redirects=True) as r:
            r.raise_for_status()
            
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            
            with open(BINARY_DEST_PATH, "wb") as f:
                downloaded_size = 0
                if total_size_in_bytes > 0:
                    print(f"合計サイズ: {total_size_in_bytes / (1024*1024):.2f} MB (約)")
                else:
                    print("合計サイズ不明。ダウンロード中...")

                for chunk in r.iter_content(chunk_size=8192):  # 8KBチャンク
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size_in_bytes > 0:
                        done = int(50 * downloaded_size / total_size_in_bytes)
                        progress_mb = downloaded_size / (1024*1024)
                        total_mb = total_size_in_bytes / (1024*1024)
                        # print(f"\r[{'=' * done}{' ' * (50-done)}] {progress_mb:.2f} MB / {total_mb:.2f} MB", end='')
                        sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {progress_mb:.2f} MB / {total_mb:.2f} MB")
                    else:  # content-lengthが利用できない場合
                        # print(f"\rダウンロード済み {downloaded_size / (1024*1024):.2f} MB", end='')
                        sys.stdout.write(f"\rダウンロード済み {downloaded_size / (1024*1024):.2f} MB")
                    sys.stdout.flush()
            sys.stdout.write("\n") # プログレスバーの後に改行
            print("バイナリファイルが正常にダウンロードされました。")
            # Make the binary executable
            BINARY_DEST_PATH.chmod(BINARY_DEST_PATH.stat().st_mode | 0o111) # Add execute permissions
            print(f"バイナリファイル {BINARY_DEST_PATH} に実行権限を付与しました。")
            
    except requests.exceptions.Timeout:
        print("バイナリファイルのダウンロードエラー: リクエストが60秒後にタイムアウトしました。")
    except requests.exceptions.RequestException as e:
        print(f"バイナリファイルのダウンロードエラー: {e}")
    except IOError as e:
        print(f"ディスクへのバイナリファイル書き込みエラー: {e}")
