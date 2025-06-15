from pathlib import Path
from src.litert_test.asset_downloader import (
    download_huggingface_model,
    download_binary_file,
    MODEL_DEST_PATH,
    BINARY_DEST_PATH,
)

# --- メイン実行 ---
if __name__ == "__main__":
    script_name = Path(__file__).name
    print(f"{script_name} を実行中...")

    try:
        download_huggingface_model()
        download_binary_file()
    except Exception as e:
        print(f"スクリプト実行中に予期せぬエラーが発生しました: {e}")

    print("\n--- 概要 ---")
    if MODEL_DEST_PATH.exists():
        print(f"モデルリポジトリの場所: {MODEL_DEST_PATH.resolve()}")
    else:
        print(
            f"モデルリポジトリ ({MODEL_DEST_PATH}) はダウンロードされなかったか、見つかりませんでした。"
        )

    if BINARY_DEST_PATH.exists():
        print(f"バイナリファイルの場所: {BINARY_DEST_PATH.resolve()}")
    else:
        print(
            f"バイナリファイル ({BINARY_DEST_PATH}) はダウンロードされなかったか、見つかりませんでした。"
        )

    print("ダウンロード処理が完了しました。")
