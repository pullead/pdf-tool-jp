# PDFオフィスツール (PDF Office Tool)

> Webブラウザ上で動作する、PDF変換・編集ツールです。  
> バックエンドには **python-office** ライブラリ（[CoderWanFeng/python-office](https://github.com/CoderWanFeng/python-office)）を利用し、**一行のコードでPDF処理**を実現しています。

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-red)](LICENSE)

---

## 📌 目次

- [プロジェクト概要](#-プロジェクト概要)
- [主な機能](#-主な機能)
- [使用技術](#-使用技術)
- [セットアップと実行](#-セットアップと実行)
- [使い方](#-使い方)
- [プロジェクト構成](#-プロジェクト構成)
- [コードの特徴・アピールポイント](#-コードの特徴アピールポイント)
- [今後の拡張予定](#-今後の拡張予定)
- [謝辞](#-謝辞)
- [ライセンス](#-ライセンス)

---

## 🎯 プロジェクト概要

**ポートフォリオ作品**として開発した、PDF実用ツールです。  
ユーザーは**ファイルをアップロード**し、**ボタンをクリック**するだけで、以下の複雑なPDF処理を実行できます。  
すべてのPDF操作は、`python-office` が提供する `popdf` モジュールの関数を**1行呼び出すだけ**で実装しており、コードの簡潔さと保守性を重視しています。

---

## ✨ 主な機能

| 機能 | 説明 | 対応メソッド（popdf） |
|------|------|----------------------|
| 📄 **PDF → Word** | PDFを編集可能なWord（.docx）に変換 | `pdf2docx` |
| 🖼️ **PDF → 画像** | 各ページを画像化（PNG/JPEG）。複数画像をZIP圧縮、または長画像に結合 | `pdf2imgs` |
| 🔗 **PDF結合** | 複数のPDFファイルを1つにまとめる | `merge2pdf` |
| ✂️ **PDF分割** | 指定したページ範囲を抽出して新しいPDFを作成 | `split4pdf` |
| 💧 **テキスト透かし** | 任意の文字列を透かしとして全ページに追加 | `add_text_watermark` |

> すべての機能はWebインターフェースから直感的に操作できます。

---

## 🛠️ 使用技術

| 層 | 技術 | 役割 |
|----|------|------|
| バックエンド | Python 3.9+, Flask | APIサーバー、ルーティング、ファイル処理 |
| PDF処理エンジン | [python-office](https://github.com/CoderWanFeng/python-office) (popdf) | 実際のPDF変換・編集処理（1行API） |
| フロントエンド | HTML5, CSS3, Bootstrap 5, JavaScript | レスポンシブなUI、非同期通信（Fetch API） |
| 一時ファイル管理 | tempfile, uuid, atexit | 安全な作業ディレクトリの作成と自動削除 |

---

## 🚀 セットアップと実行

### 1. リポジトリのクローン

```bash
git clone https://github.com/pullead/pdf-tool-jp.git
cd pdf-tool-jp
```
### 2. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```
requirements.txt の中身:
```text
flask==2.3.3
python-office==1.0.6
Werkzeug==2.3.7
```
### 3. アプリケーションの起動
```bash
python backend/app.py
```
以下のようなメッセージが表示されれば成功です。
```text
* Running on http://127.0.0.1:5000
```
### 4. ブラウザでアクセス 
http://localhost:5000
を開き、ツールを使用します。

## 📖 使い方
### 1.PDFをアップロード

   🔗左側の「PDFアップロード」エリアにファイルをドラッグ＆ドロップ、またはクリックして選択します。

🔗アップロードが完了するとファイル名が表示されます。

### 2.処理を選択

   🔗右側の「処理メニュー」から希望の機能ボタンをクリックします。

🔗分割・透かし追加の場合は、ポップアップ（モーダル）で詳細設定（ページ範囲や透かし文字）を入力します。

### 3.結果をダウンロード

   🔗処理が完了すると、自動的に変換・編集されたファイルのダウンロードが開始されます。

🔗結合機能のみ、複数ファイル選択後に「結合実行」ボタンを押します。

💡 ヒント: アップロード後はいつでも別の機能を試せます。処理ごとに新しいファイルが生成されます。

## 📁 プロジェクト構成
```text
pdf-tool-jp/
├── backend/
│   ├── app.py                 # Flaskメインアプリ（エンドポイント定義）
│   ├── pdf_handler.py         # python-office(popdf)のラッパー関数
│   └── temp_manager.py        # 一時ディレクトリの作成・削除
├── frontend/
│   ├── index.html             # ユーザーインターフェース（日本語UI）
│   ├── style.css              # スタイルシート（ダーク/ライト対応）
│   └── script.js              # フロントエンドの非同期通信とDOM操作
├── requirements.txt           # Python依存パッケージ一覧
└── README.md                  # このファイル
```
## 💡 コードの特徴・アピールポイント
### ✅ 1. 外部ライブラリの効果的な活用
⭐複雑なPDF処理を python-office の一行API に委譲。

⭐例: pdf.pdf2docx(input_file=input_path, output_file=output_file)

⭐車輪の再発明を避け、信頼性と開発速度を両立。
### ✅ 2. クリーンな関心の分離
⭐pdf_handler.py … PDF処理ロジック

⭐app.py … HTTPリクエスト/レスポンス制御

⭐temp_manager.py … ファイルライフサイクル管理

⭐変更に強く、テストしやすい構造。
### ✅ 3. 堅牢な一時ファイル管理
⭐tempfile.mkdtemp + uuid でリクエストごとにユニークな作業ディレクトリを生成。

⭐atexit を利用してプログラム終了時にルート一時ディレクトリを自動削除。

⭐サーバーのディスク消費を防止。
### ✅ 4. ユーザーフレンドリーなUI
⭐ドラッグ＆ドロップによる直感的なアップロード。

⭐処理中のプログレスバー表示。

⭐ページ範囲や透かし文字を設定するモーダルダイアログ。

⭐すべてのテキストは日本語で表示。
### ✅ 5. エラーハンドリングとフィードバック
⭐アップロード失敗、非PDFファイル、処理エラーなどを適切に検知し、ユーザーにアラート表示。

⭐HTTPステータスコードとJSONエラーメッセージでクライアントに詳細を通知。
## 🔮 今後の拡張予定
💡PDF暗号化・復号（encrypt4pdf / decrypt4pdf）

💡画像ウォーターマーク対応（add_img_water）

💡バッチ処理（複数ファイル一括変換）

💡Dockerコンテナ化（環境依存ゼロ）

💡処理履歴と一括ダウンロード機能
## 🙏 謝辞
本プロジェクトは、CoderWanFeng 氏が開発・公開している python-office ライブラリの popdf モジュールに深く依存しています。
自動化オフィス処理の敷居を劇的に下げたこのOSSに、心より敬意と感謝を表します。

👤GitHub: https://github.com/CoderWanFeng/python-office

👤公式サイト: https://www.python-office.com
## 📜 ライセンス
このプロジェクトは MITライセンス の下で公開されています。
python-office ライブラリも同様にMITライセンスです。

## 👤 作者
⭐GitHubユーザー名: pullead

⭐連絡先: （pullead@gmail.com）
