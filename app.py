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
    """PDFからテキストを抽出する基本OCR機能（デバッグ版）"""
    debug_info = []
    
    try:
        debug_info.append("Step 1: ライブラリのインポート開始")
        
        import pytesseract
        debug_info.append("✅ pytesseract インポート成功")
        
        from pdf2image import convert_from_path
        debug_info.append("✅ pdf2image インポート成功")
        
        from PIL import Image
        debug_info.append("✅ PIL インポート成功")
        
        debug_info.append(f"Step 2: PDF変換開始 - ファイル: {filepath}")
        
        # PDF→画像変換
        images = convert_from_path(filepath)
        debug_info.append(f"✅ PDF変換完了 - {len(images)}ページ")
        
        if len(images) == 0:
            return "❌ PDFから画像を取得できませんでした"
        
        debug_info.append("Step 3: OCR処理開始")
        
        extracted_text = ""
        for i, image in enumerate(images):
            debug_info.append(f"ページ {i+1} を処理中...")
            
            # まずは英語でテスト（日本語でエラーが出る場合）
            try:
                text = pytesseract.image_to_string(image, lang='jpn')
                debug_info.append(f"✅ ページ {i+1} 日本語OCR成功")
            except:
                text = pytesseract.image_to_string(image, lang='eng')
                debug_info.append(f"⚠️ ページ {i+1} 英語OCRで代用")
            
            extracted_text += f"=== ページ {i+1} ===\n{text}\n\n"
            
            # 最初のページで処理を停止（テスト用）
            if i == 0:
                break
        
        debug_info.append("Step 4: 結果保存")
        
        # 結果をファイルに保存（デバッグ用）
        result_file = filepath.replace('.pdf', '_ocr_result.txt')
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        debug_info.append(f"✅ 結果ファイル保存: {result_file}")
        
        return f"✅ OCR処理完了！\n\nデバッグ情報:\n" + "\n".join(debug_info) + f"\n\n認識されたテキスト（最初の200文字）:\n{extracted_text[:200]}..."
        
    except ImportError as e:
        return f"❌ ライブラリエラー: {str(e)}\n\nデバッグ情報:\n" + "\n".join(debug_info)
    except Exception as e:
        return f"❌ OCR処理エラー: {str(e)}\n\nデバッグ情報:\n" + "\n".join(debug_info)

@app.route('/test')
def test():
    return "🎉 Flask アプリケーションが正常に動作しています！"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
