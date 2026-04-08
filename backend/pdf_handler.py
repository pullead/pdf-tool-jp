# -*- coding: utf-8 -*-
"""PDF処理機能 - python-officeライブラリのpopdfモジュールを呼び出します。"""

import os
import zipfile
from pathlib import Path
from office.api import pdf  # python-officeのpopdfモジュールをインポート


def pdf_to_word(input_path: str, output_dir: str) -> str:
    """
    PDFファイルをWord（.docx）ファイルに変換します。

    Args:
        input_path (str): 入力PDFファイルのパス
        output_dir (str): 出力ディレクトリのパス

    Returns:
        str: 生成されたWordファイルのパス
    """
    output_file = os.path.join(output_dir, Path(input_path).stem + ".docx")
    # popdfのpdf2docx関数を1行で呼び出し
    pdf.pdf2docx(input_file=input_path, output_file=output_file)
    return output_file


def pdf_to_images(input_path: str, output_dir: str, merge: bool = False) -> str:
    """
    PDFファイルを画像に変換します。
    - merge=True: 1枚の長い画像（PNG）として出力
    - merge=False: 各ページを個別の画像としてZIP圧縮

    Args:
        input_path (str): 入力PDFファイルのパス
        output_dir (str): 出力ディレクトリのパス
        merge (bool): 長画像に結合するかどうか

    Returns:
        str: 生成された画像ファイルまたはZIPファイルのパス
    """
    if merge:
        # 長画像として出力
        output_path = os.path.join(output_dir, Path(input_path).stem + "_long.png")
        pdf.pdf2imgs(input_file=input_path, output_file=output_path, merge=True)
        return output_path
    else:
        # 個別画像を一時ディレクトリに出力
        img_dir = os.path.join(output_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        pdf.pdf2imgs(input_file=input_path, output_file=img_dir, merge=False)

        # 画像群をZIPに圧縮
        zip_path = os.path.join(output_dir, Path(input_path).stem + "_images.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(img_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, img_dir)
                    zipf.write(full_path, arcname)
        return zip_path


def merge_pdfs(file_paths: list, output_dir: str, output_name: str = "merged.pdf") -> str:
    """
    複数のPDFファイルを1つに結合します。

    Args:
        file_paths (list): 結合するPDFファイルのパスリスト
        output_dir (str): 出力ディレクトリのパス
        output_name (str): 出力ファイル名

    Returns:
        str: 結合されたPDFファイルのパス
    """
    output_path = os.path.join(output_dir, output_name)
    # popdfのmerge2pdf関数を呼び出し
    pdf.merge2pdf(input_file_list=file_paths, output_file=output_path)
    return output_path


def split_pdf(input_path: str, output_dir: str, from_page: int, to_page: int) -> str:
    """
    PDFファイルから指定されたページ範囲を抽出（分割）します。

    Args:
        input_path (str): 入力PDFファイルのパス
        output_dir (str): 出力ディレクトリのパス
        from_page (int): 開始ページ
        to_page (int): 終了ページ（-1は最終ページを意味する）

    Returns:
        str: 分割されたPDFファイルのパス
    """
    output_name = f"{Path(input_path).stem}_p{from_page}-{to_page}.pdf"
    output_path = os.path.join(output_dir, output_name)
    pdf.split4pdf(input_file=input_path, output_file=output_path,
                  from_page=from_page, to_page=to_page)
    return output_path


def add_watermark(input_path: str, output_dir: str, text: str) -> str:
    """
    PDFファイルにテキストの透かしを追加します。

    Args:
        input_path (str): 入力PDFファイルのパス
        output_dir (str): 出力ディレクトリのパス
        text (str): 透かしテキスト

    Returns:
        str: 透かし入りPDFファイルのパス
    """
    output_path = os.path.join(output_dir, f"{Path(input_path).stem}_watermarked.pdf")
    pdf.add_text_watermark(input_file=input_path, text=text, output_file=output_path)
    return output_path