document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const progress = document.getElementById('progress');
    const result = document.getElementById('result');

    // クリックでファイル選択
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // ファイル選択時の処理
    fileInput.addEventListener('change', handleFile);

    // ドラッグ&ドロップ
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#e9ecef';
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f8f9fa';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f8f9fa';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile({ target: { files: files } });
        }
    });

    function handleFile(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (file.type !== 'application/pdf') {
            showResult('PDFファイルを選択してください', 'error');
            return;
        }

        uploadFile(file);
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        progress.style.display = 'block';
        const progressBar = progress.querySelector('.progress-bar');

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showResult(data.message, 'success');
            } else {
                showResult(data.error, 'error');
            }
        })
        .catch(error => {
            showResult('アップロードエラーが発生しました', 'error');
        })
        .finally(() => {
            progress.style.display = 'none';
        });
    }

    function showResult(message, type) {
        result.textContent = message;
        result.className = `result ${type}`;
        result.style.display = 'block';
    }
});
