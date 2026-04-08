# -*- coding: utf-8 -*-
"""一時ファイル管理モジュール（自動クリーンアップ機能付き）"""

import shutil
import tempfile
import atexit
import uuid
from pathlib import Path

# グローバルな一時ルートディレクトリ（プログラム終了時に自動削除）
TEMP_ROOT = Path(tempfile.mkdtemp(prefix="pdf_tool_jp_"))
atexit.register(lambda: shutil.rmtree(TEMP_ROOT, ignore_errors=True))


def create_temp_dir() -> Path:
    """
    リクエストごとに一意の一時ディレクトリを作成します。

    Returns:
        Path: 作成された一時ディレクトリのパス
    """
    dir_path = TEMP_ROOT / str(uuid.uuid4())
    dir_path.mkdir(parents=True)
    return dir_path


def cleanup_temp_dir(dir_path: Path):
    """
    指定された一時ディレクトリを削除します。

    Args:
        dir_path (Path): 削除するディレクトリのパス
    """
    if dir_path.exists():
        shutil.rmtree(dir_path, ignore_errors=True)