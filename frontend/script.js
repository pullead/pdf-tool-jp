// グローバル変数
let currentFileId = null;
let currentFileName = null;

// DOM要素の取得
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const uploadFilenameSpan = document.getElementById('upload-filename');

// ドラッグ＆ドロップ領域のイベント設定
dropArea.addEventListener('click', () => fileInput.click());
dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.classList.add('drag-over');
});
dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drag-over'));
dropArea.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length) await uploadFile(files[0]);
});

fileInput.addEventListener('change', async (e) => {
    if (e.target.files.length) await uploadFile(e.target.files[0]);
});

/**
 * PDFファイルをアップロードする
 * @param {File} file - アップロードするPDFファイル
 */
async function uploadFile(file) {
    if (!file.name.endsWith('.pdf')) {
        alert('PDFファイルのみアップロード可能です。');
        return;
    }
    const formData = new FormData();
    formData.append('file', file);
    showProgress('アップロード中...');
    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        hideProgress();
        if (res.ok) {
            currentFileId = data.file_id;
            currentFileName = data.original_name;
            uploadFilenameSpan.innerText = currentFileName;
            fileInfo.style.display = 'block';
            document.getElementById('merge-btn').disabled = false;
        } else {
            alert('アップロード失敗: ' + data.error);
        }
    } catch (err) {
        hideProgress();
        alert('ネットワークエラーが発生しました。');
    }
}

/** アップロード済みファイル情報をリセットする */
function resetFile() {
    currentFileId = null;
    currentFileName = null;
    fileInfo.style.display = 'none';
    fileInput.value = '';
    document.getElementById('merge-btn').disabled = true;
}

/**
 * 選択されたアクションを実行する
 * @param {string} action - 実行するアクション名
 * @param {object} params - アクションに渡す追加パラメータ
 * @returns {Promise<boolean>} 成功したらtrue
 */
async function performAction(action, params = {}) {
    if (!currentFileId) {
        alert('先にPDFファイルをアップロードしてください。');
        return false;
    }
    showProgress('処理実行中...');
    try {
        const response = await fetch('/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: currentFileId, action, params })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || '処理に失敗しました。');
        }
        // レスポンスをBlobとしてダウンロード
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        let filename = '';
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.includes('filename=')) {
            filename = disposition.split('filename=')[1].replace(/["']/g, '');
        } else {
            filename = `output_${action}.pdf`;
        }
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        hideProgress();
        alert('処理が完了しました。ダウンロードを開始します。');
        return true;
    } catch (err) {
        hideProgress();
        alert('エラー: ' + err.message);
        return false;
    }
}

// 複数ファイル結合の処理
document.getElementById('merge-input').addEventListener('change', () => {
    const input = document.getElementById('merge-input');
    document.getElementById('merge-btn').disabled = input.files.length < 2;
});
document.getElementById('merge-btn').addEventListener('click', async () => {
    const input = document.getElementById('merge-input');
    const files = input.files;
    if (files.length < 2) {
        alert('少なくとも2つ以上のPDFファイルを選択してください。');
        return;
    }
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    showProgress('結合中...');
    try {
        const res = await fetch('/merge', { method: 'POST', body: formData });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error);
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'merged.pdf';
        a.click();
        URL.revokeObjectURL(url);
        hideProgress();
        alert('結合が完了しました。');
    } catch (err) {
        hideProgress();
        alert('結合失敗: ' + err.message);
    }
});

// 各アクションボタンのイベント設定
document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', async () => {
        const action = btn.dataset.action;
        if (action === 'to_images') {
            const merge = btn.dataset.merge === 'true';
            await performAction(action, { merge });
        } else if (action === 'to_word') {
            await performAction(action);
        }
    });
});

// 分割確認ボタン
document.getElementById('confirm-split').addEventListener('click', async () => {
    let from = parseInt(document.getElementById('split-from').value);
    let to = parseInt(document.getElementById('split-to').value);
    if (isNaN(from)) from = 1;
    if (isNaN(to)) to = -1;
    const modal = bootstrap.Modal.getInstance(document.getElementById('splitModal'));
    modal.hide();
    await performAction('split', { from_page: from, to_page: to });
});

// 透かし確認ボタン
document.getElementById('confirm-watermark').addEventListener('click', async () => {
    const text = document.getElementById('watermark-text').value.trim();
    if (!text) {
        alert('透かし文字を入力してください。');
        return;
    }
    const modal = bootstrap.Modal.getInstance(document.getElementById('watermarkModal'));
    modal.hide();
    await performAction('watermark', { text });
});

/** プログレス表示を表示する */
function showProgress(msg) {
    const progDiv = document.getElementById('progress');
    const progBar = progDiv.querySelector('.progress-bar');
    progBar.style.width = '100%';
    progBar.innerText = msg;
    progDiv.style.display = 'block';
}

/** プログレス表示を隠す */
function hideProgress() {
    document.getElementById('progress').style.display = 'none';
}