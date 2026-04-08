# -*- coding: utf-8 -*-
"""Flaskメインアプリケーション - PDF処理ツールのAPIエンドポイントを提供します。"""

import os
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pdf_handler import *
from temp_manager import create_temp_dir, cleanup_temp_dir

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # アップロード上限: 50MB

# アップロードされたファイル情報を一時保存 {file_id: {"path": "元ファイルパス", "temp_dir": "一時ディレクトリ"}}
uploaded_files = {}


@app.route('/upload', methods=['POST'])
def upload_file():
    """PDFファイルをアップロードし、一意のfile_idを返します。"""
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400

    temp_dir = create_temp_dir()
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.pdf'):
        return jsonify({'error': 'PDFファイルのみ許可されています'}), 400

    file_path = temp_dir / filename
    file.save(file_path)

    file_id = str(file_path.stem) + "_" + os.urandom(4).hex()
    uploaded_files[file_id] = {
        "path": str(file_path),
        "temp_dir": temp_dir,
        "original_name": filename
    }
    return jsonify({'file_id': file_id, 'original_name': filename})


@app.route('/convert', methods=['POST'])
def convert():
    """
    アップロード済みファイルに対して指定された処理（変換・分割・透かし等）を実行します。
    処理結果のファイルをダウンロード可能な形式で返します。
    """
    data = request.get_json()
    file_id = data.get('file_id')
    action = data.get('action')
    params = data.get('params', {})

    if file_id not in uploaded_files:
        return jsonify({'error': '無効なfile_idです'}), 400

    file_info = uploaded_files[file_id]
    input_path = file_info['path']
    output_dir = create_temp_dir()  # 結果格納用の新しい一時ディレクトリ

    try:
        if action == 'to_word':
            out_path = pdf_to_word(input_path, output_dir)
        elif action == 'to_images':
            merge = params.get('merge', False)
            out_path = pdf_to_images(input_path, output_dir, merge)
        elif action == 'split':
            from_page = params.get('from_page', 1)
            to_page = params.get('to_page', -1)
            out_path = split_pdf(input_path, output_dir, from_page, to_page)
        elif action == 'watermark':
            text = params.get('text', 'python-office')
            out_path = add_watermark(input_path, output_dir, text)
        else:
            return jsonify({'error': '不明なアクションです'}), 400

        # 処理結果のファイルをクライアントに送信（ダウンロード）
        return send_file(out_path, as_attachment=True,
                         download_name=os.path.basename(out_path))

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # 元のアップロードファイルの一時ディレクトリをクリーンアップ
        cleanup_temp_dir(file_info['temp_dir'])
        del uploaded_files[file_id]


@app.route('/merge', methods=['POST'])
def merge():
    """複数のPDFファイルを結合します。"""
    if 'files' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400
    files = request.files.getlist('files')
    if len(files) < 2:
        return jsonify({'error': '少なくとも2つ以上のPDFファイルが必要です'}), 400

    temp_dir = create_temp_dir()
    pdf_paths = []
    for f in files:
        if f.filename and f.filename.lower().endswith('.pdf'):
            safe_name = secure_filename(f.filename)
            path = temp_dir / safe_name
            f.save(path)
            pdf_paths.append(str(path))
        else:
            return jsonify({'error': 'PDFファイルのみ許可されています'}), 400

    output_dir = create_temp_dir()
    try:
        out_path = merge_pdfs(pdf_paths, output_dir, "merged.pdf")
        return send_file(out_path, as_attachment=True, download_name="merged.pdf")
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_temp_dir(temp_dir)


# フロントエンドファイルを配信するためのルート（開発用）
@app.route('/')
def index():
    from flask import send_from_directory
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    from flask import send_from_directory
    return send_from_directory('../frontend', filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)