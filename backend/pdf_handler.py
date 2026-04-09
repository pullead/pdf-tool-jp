# -*- coding: utf-8 -*-
"""PDF処理機能（PyMuPDF + popdf）"""

import io
import os
import zipfile
from pathlib import Path

import popdf
import fitz  # PyMuPDF
from PIL import Image


def pdf_to_word(input_path: str, output_dir: str) -> str:
    """PDF → Word"""
    output_file = os.path.join(output_dir, Path(input_path).stem + ".docx")
    popdf.pdf2docx(input_file=input_path, output_path=output_file)
    return output_file


def pdf_to_images(input_path: str, output_dir: str, merge: bool = False) -> str:
    """
    PDF → 画像（PyMuPDF を使用、poppler 不要）
    merge=True  → 1枚の長画像（PNG）
    merge=False → 各ページを個別画像にしてZIP圧縮
    """
    input_path = str(input_path)
    output_dir = str(output_dir)

    doc = fitz.open(input_path)
    images = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        zoom = 200 / 72  # 200 dpi
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        images.append(img)

    doc.close()

    if merge:
        total_height = sum(img.height for img in images)
        max_width = max(img.width for img in images)
        combined = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for img in images:
            combined.paste(img, (0, y_offset))
            y_offset += img.height
        output_path = os.path.join(output_dir, Path(input_path).stem + "_long.png")
        combined.save(output_path)
        return output_path
    else:
        img_dir = os.path.join(output_dir, "images")
        os.makedirs(img_dir, exist_ok=True)
        for i, img in enumerate(images):
            img.save(os.path.join(img_dir, f"page_{i+1}.png"))
        zip_path = os.path.join(output_dir, Path(input_path).stem + "_images.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(img_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, img_dir)
                    zipf.write(full_path, arcname)
        return zip_path


def merge_pdfs(file_paths: list, output_dir: str, output_name: str = "merged.pdf") -> str:
    output_path = os.path.join(output_dir, output_name)
    popdf.merge2pdf(input_file_list=file_paths, output_file=output_path)
    return output_path


def split_pdf(input_path: str, output_dir: str, from_page: int, to_page: int) -> str:
    output_name = f"{Path(input_path).stem}_p{from_page}-{to_page}.pdf"
    output_path = os.path.join(output_dir, output_name)
    popdf.split4pdf(input_file=input_path, output_file=output_path,
                    from_page=from_page, to_page=to_page)
    return output_path


def add_watermark(input_path: str, output_dir: str, text: str) -> str:
    output_path = os.path.join(output_dir, f"{Path(input_path).stem}_watermarked.pdf")
    # point は水印の座標（例: (50, 50)）。必要に応じて変更可能
    popdf.add_text_watermark(
        input_file=input_path,
        point=(50, 50),          # ← 必須なので追加
        text=text,
        output_file=output_path,
        fontname="Helvetica",
        fontsize=12,
        color=(1, 0, 0)          # 赤色
    )
    return output_path