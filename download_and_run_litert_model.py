import argparse
from pathlib import Path
import sys

try:
    from src.litert_test.asset_downloader import (
        download_huggingface_model,
        download_binary_file,
        MODEL_DEST_PATH,
        BINARY_DEST_PATH,
    )
    from src.litert_test.model_runner import run_litert_model
except ImportError:
    print("エラー: 必要なモジュール (src.litert_test.asset_downloader または src.litert_test.model_runner) が見つかりません。")
    print("スクリプトがプロジェクトのルートディレクトリから実行されているか、PYTHONPATHが正しく設定されているか確認してください。")
    sys.exit(1)

def main():
    script_name = Path(__file__).name
    print(f"{script_name} を実行中...")

    parser = argparse.ArgumentParser(description="LiteRT-LMモデルのアセットをダウンロードし、実行します。")

    # --- ダウンロード関連の引数 ---
    parser.add_argument(
        "--skip_download",
        action="store_true",
        help="アセットのダウンロードをスキップします。既存のファイルを使用するか、パス引数で指定する場合に便利です。"
    )

    # --- モデル実行関連の引数 (run_litert_model.py から) ---
    # model_path と binary_path はデフォルトでダウンロード先を参照するように変更
    parser.add_argument(
        "--binary_path",
        type=str,
        default=None,
        help=f"litert_lm_main 実行可能ファイルへのパス。指定しない場合、デフォルトの場所 ({BINARY_DEST_PATH}) にダウンロード/使用されます。"
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default=None,
        help=f".litertlm モデルファイルへのパス。指定しない場合、デフォルトの場所 ({MODEL_DEST_PATH}) にダウンロード/使用されます。"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="日本の首都はどこですか？",
        help="モデルへの入力プロンプト。benchmark_prefill_tokens > 0 の場合は無視されます。"
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="cpu",
        choices=["cpu", "gpu"],
        help="使用するバックエンド (cpu または gpu)。"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="ベンチマークモードで実行します。"
    )
    parser.add_argument(
        "--benchmark_prefill_tokens",
        type=int,
        default=0,
        help="ベンチマーク用のプリフィル トークン数。 > 0 の場合、async は false に設定されます。"
    )
    parser.add_argument(
        "--benchmark_decode_tokens",
        type=int,
        default=0,
        help="ベンチマーク用のデコード トークン数。"
    )
    parser.add_argument(
        "--async_mode",
        type=lambda x: (str(x).lower() == 'true'), # "true"/"false" を bool に変換
        default=True,
        help="LLMを非同期で実行します (true/false)。benchmark_prefill_tokens > 0 の場合は false に上書きされます。"
    )
    parser.add_argument(
        "--show_stderr",
        action="store_true",
        help="モデル実行からのstderr出力を常に表示します。デフォルトでは、stdoutがない場合やエラーが疑われる場合にのみ表示されます。"
    )

    args = parser.parse_args()

    # --- アセットのパスを決定し、必要に応じてダウンロード ---
    # final_model_path は後で .litertlm ファイルを探索して設定する
    # args.model_path が指定されていれば、それが最終的なファイルパスであると仮定する
    # そうでなければ、ダウンロード後に MODEL_DEST_PATH から探す
    final_model_path = Path(args.model_path) if args.model_path else None
    final_binary_path = Path(args.binary_path) if args.binary_path else BINARY_DEST_PATH

    if not args.skip_download:
        print("\n--- アセットのダウンロード処理を開始します ---")
        try:
            # モデルのダウンロード (ユーザーがパスを指定していない場合)
            if not args.model_path:
                model_dir_exists = MODEL_DEST_PATH.exists() and MODEL_DEST_PATH.is_dir()
                if not model_dir_exists:
                    print(f"HuggingFaceモデルを {MODEL_DEST_PATH} にダウンロード中...")
                    download_huggingface_model()
                    if MODEL_DEST_PATH.exists() and MODEL_DEST_PATH.is_dir():
                        print(f"モデルリポジトリのダウンロード完了: {MODEL_DEST_PATH.resolve()}")
                        model_dir_exists = True
                    else:
                        print(f"エラー: モデルリポジトリ ({MODEL_DEST_PATH}) のダウンロードに失敗しました。")
                        return # 処理を中断
                else:
                    print(f"モデルリポジトリは既に存在します: {MODEL_DEST_PATH.resolve()}")

                if model_dir_exists:
                    # MODEL_DEST_PATH 内の .litertlm ファイルを探索
                    litertlm_files = list(MODEL_DEST_PATH.glob("*.litertlm"))
                    if len(litertlm_files) == 1:
                        final_model_path = litertlm_files[0]
                        print(f"モデルファイルを発見: {final_model_path.resolve()}")
                    elif len(litertlm_files) == 0:
                        print(f"エラー: {MODEL_DEST_PATH} 内に .litertlm ファイルが見つかりません。")
                        return
                    else:
                        print(f"エラー: {MODEL_DEST_PATH} 内に複数の .litertlm ファイルが見つかりました。使用するファイルを --model_path で指定してください。")
                        for f in litertlm_files:
                            print(f"  - {f}")
                        return
            else:
                print(f"指定されたモデルパスを使用します: {final_model_path.resolve() if final_model_path else '未指定'}")

            # バイナリファイルのダウンロード (ユーザーがパスを指定していない場合)
            if not args.binary_path:
                if not BINARY_DEST_PATH.exists():
                    print(f"バイナリファイルを {BINARY_DEST_PATH} にダウンロード中...")
                    download_binary_file()
                    if BINARY_DEST_PATH.exists():
                        print(f"バイナリファイルのダウンロード完了: {BINARY_DEST_PATH.resolve()}")
                    else:
                        print(f"エラー: バイナリファイル ({BINARY_DEST_PATH}) のダウンロードに失敗しました。")
                        return # 処理を中断
                else:
                    print(f"バイナリファイルは既に存在します: {BINARY_DEST_PATH.resolve()}")
            else:
                print(f"指定されたバイナリパスを使用します: {final_binary_path.resolve()}")
            print("--- アセットのダウンロード処理が完了しました ---")
        except Exception as e:
            print(f"アセットダウンロード中に予期せぬエラーが発生しました: {e}")
            # ダウンロードエラー時、パスの存在確認は後続の処理で行う
    else:
        print("\n--- アセットのダウンロードはスキップされました ---")
        if not final_model_path and MODEL_DEST_PATH.exists() and MODEL_DEST_PATH.is_dir():
            # スキップされたが、デフォルトのモデルディレクトリが存在する場合、そこから探す
            litertlm_files = list(MODEL_DEST_PATH.glob("*.litertlm"))
            if len(litertlm_files) == 1:
                final_model_path = litertlm_files[0]
                print(f"既存のモデルファイルを使用: {final_model_path.resolve()}")

    # 最終的なパスの存在確認
    if not final_model_path or not final_model_path.exists() or not final_model_path.is_file():
        print(f"エラー: モデルファイルが見つかりません、または有効なファイルではありません: {final_model_path.resolve() if final_model_path else 'パスが解決できませんでした'}")
        print("ダウンロードが失敗したか、正しいパスが指定されていないか、.litertlm ファイルがディレクトリ内に存在しない可能性があります。")
        return
    if not final_binary_path.exists():
        print(f"エラー: バイナリファイルが見つかりません: {final_binary_path.resolve()}")
        print("ダウンロードが失敗したか、正しいパスが指定されていないか、--skip_download が不適切に使用された可能性があります。")
        return

    # --- モデル実行 ---
    print("\n--- LiteRT-LMモデルの実行を開始します ---")

    current_async_mode = args.async_mode
    if args.benchmark and args.benchmark_prefill_tokens > 0 and args.async_mode:
        current_async_mode = False
        print("注意: benchmark_prefill_tokens > 0 のため、非同期モードは False に設定されました。")

    try:
        stdout, stderr = run_litert_model(
            str(final_binary_path.resolve()), # Pathオブジェクトを文字列に変換
            str(final_model_path.resolve()),   # Pathオブジェクトを文字列に変換
            args.prompt,
            args.backend,
            args.benchmark,
            args.benchmark_prefill_tokens,
            args.benchmark_decode_tokens,
            current_async_mode
        )

        if stdout:
            print("\n--- モデル出力 (stdout) ---")
            print(stdout)
        # stderr は stdout がない場合、エラーが疑われる場合、または明示的に表示が要求された場合にのみ表示
        if stderr and (not stdout or args.show_stderr):
            print("\n--- モデル情報/エラー (stderr) ---")
            print(stderr)
            print("\nエラーが発生した可能性があります。上記のstderr出力を確認してください。")
        
        if not stdout and not stderr:
            print("モデル実行からの出力がありませんでした。")

    except Exception as e:
        print(f"モデル実行中に予期せぬエラーが発生しました: {e}")

    print("\n--- 最終的なパスの概要 ---")
    print(f"使用されたモデルファイルの場所: {final_model_path.resolve()}")
    print(f"使用されたバイナリファイルの場所: {final_binary_path.resolve()}")

if __name__ == "__main__":
    main()
    print(f"\n{Path(__file__).name} の実行が完了しました。")