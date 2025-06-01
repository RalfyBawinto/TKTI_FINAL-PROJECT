import os
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from PyPDF2 import PdfReader
import io

app = Flask(__name__)
CORS(app)

def summarize_with_huggingface(text):
    api_token = os.getenv("HF_API_TOKEN")
    api_url = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
    headers = {"Authorization": f"Bearer {api_token}"}

    response = requests.post(api_url, headers=headers, json={"inputs": text})
    if response.status_code == 200:
        result = response.json()
        return result[0]['summary_text']
    else:
        return "Ringkasan gagal."

@app.route('/analyze', methods=['POST'])
def analyze_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang di-upload'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nama file kosong'}), 400
    
    try:
        reader = PdfReader(file.stream)
    except Exception as e:
        return jsonify({'error': f'Gagal membaca file PDF: {str(e)}'}), 400

    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''

    max_len = 1000
    chunk = text[:max_len]

    summary = summarize_with_huggingface(chunk)
    return jsonify({'summary': summary})

# Route untuk menampilkan halaman frontend
@app.route('/')
def home():
    return render_template('index.html')

# Route untuk melayani file statis (js, css)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
