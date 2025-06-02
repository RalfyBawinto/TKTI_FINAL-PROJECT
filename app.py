import os
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS
from PyPDF2 import PdfReader

app = Flask(__name__)

# ✅ CORS config — hanya izinkan dari GitHub Pages
CORS(app, resources={r"/analyze": {"origins": "https://ralfybawinto.github.io"}}, supports_credentials=True)

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

# ✅ Tambahkan OPTIONS handler untuk preflight
@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_pdf():
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = 'https://ralfybawinto.github.io'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

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

    # ✅ Tambahkan header CORS manual ke response
    response = jsonify({'summary': summary})
    response.headers.add("Access-Control-Allow-Origin", "https://ralfybawinto.github.io")
    return response

# Frontend route (optional kalau hanya API)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
