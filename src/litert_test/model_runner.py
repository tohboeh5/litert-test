import subprocess
import os
import stat

def run_litert_model(binary_path: str, model_path: str, prompt: str, backend: str = "cpu", benchmark: bool = False, prefill_tokens: int = 0, decode_tokens: int = 0, async_mode: bool = True) -> tuple[str | None, str | None]:
    """
    LiteRT-LMモデルをコマンドラインバイナリ経由で実行します。

    Args:
        binary_path (str): litert_lm_main 実行可能ファイルへのパス。
        model_path (str): .litertlm モデルファイルへのパス。
        prompt (str): モデルへの入力プロンプト。
        backend (str): バックエンド ("cpu" または "gpu")。
        benchmark (bool): ベンチマークモードで実行するかどうか。
        prefill_tokens (int): ベンチマーク用のプリフィル トークン数。
        decode_tokens (int): ベンチマーク用のデコード トークン数。
        async_mode (bool): 非同期モードで実行するかどうか。

    Returns:
        tuple: (stdout, stderr) サブプロセス実行結果。
    """
    if not os.path.exists(binary_path):
        raise FileNotFoundError(f"LiteRT-LM バイナリが見つかりません: {binary_path}")

    # バイナリに実行権限があるか確認し、なければ付与を試みる (Unix系)
    if not os.access(binary_path, os.X_OK):
        try:
            current_permissions = os.stat(binary_path).st_mode
            os.chmod(binary_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print(f"実行権限を付与しました: {binary_path}")
        except OSError as e:
            raise PermissionError(
                f"LiteRT-LM バイナリに実行権限がありません。また、付与できませんでした: {binary_path}. "
                f"手動で実行権限を付与してください。エラー: {e}"
            )

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}")

    command = [
        binary_path,
        "--model_path", model_path,
        "--backend", backend,
    ]

    effective_async_mode = async_mode
    if benchmark and prefill_tokens > 0:
        # LiteRT-LMドキュメントより: benchmark_prefill_tokens > 0 の場合、async は false である必要があります。
        effective_async_mode = False

    command.extend(["--async", str(effective_async_mode).lower()])

    if benchmark:
        command.extend(["--benchmark", "true"])
        if prefill_tokens > 0:
            command.extend(["--benchmark_prefill_tokens", str(prefill_tokens)])
        if decode_tokens > 0:
            command.extend(["--benchmark_decode_tokens", str(decode_tokens)])
        if prefill_tokens == 0 and prompt:
            command.extend(["--input_prompt", prompt])
    elif prompt: # 非ベンチマークモード
        command.extend(["--input_prompt", prompt])

    print(f"コマンド実行: {' '.join(command)}")
    process = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8')
    return process.stdout, process.stderr