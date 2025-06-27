from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB制限

# アップロードフォルダ作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルが選択されていません'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'})
    
    if file and file.filename.lower().endswith('.pdf'):
        filename = f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # OCR処理を実行
        try:
            ocr_result = process_pdf_ocr(filepath)
            return jsonify({
                'success': True, 
                'message': f'✅ ファイルをアップロードしました: {filename}',
                'filename': filename,
                'ocr_result': ocr_result
            })
        except Exception as e:
            return jsonify({
                'success': True, 
                'message': f'✅ ファイルをアップロードしました: {filename}',
                'filename': filename,
                'ocr_result': f'OCR処理でエラーが発生しました: {str(e)}'
            })
    
    return jsonify({'error': '❌ PDFファイルのみ対応しています'})

def process_pdf_ocr(filepath):
    """PDFからテキストを抽出する基本OCR機能"""
    try:
        # まずは基本的なOCRライブラリの動作確認
        import pytesseract
        from pdf2image import convert_from_path
        from PIL import Image
        
        # PDF→画像変換
        images = convert_from_path(filepath)
        
        extracted_text = ""
        for i, image in enumerate(images):
            # OCRでテキスト抽出
            text = pytesseract.image_to_string(image, lang='jpn')
            extracted_text += f"=== ページ {i+1} ===\n{text}\n\n"
        
        # 結果をファイルに保存（デバッグ用）
        result_file = filepath.replace('.pdf', '_ocr_result.txt')
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        return f"✅ OCR処理完了！{len(images)}ページを処理しました。\n\n認識されたテキスト（最初の500文字）:\n{extracted_text[:500]}..."
        
    except ImportError as e:
        return f"❌ 必要なライブラリがインストールされていません: {str(e)}"
    except Exception as e:
        return f"❌ OCR処理中にエラーが発生しました: {str(e)}"

@app.route('/test')
def test():
    return "🎉 Flask アプリケーションが正常に動作しています！"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
