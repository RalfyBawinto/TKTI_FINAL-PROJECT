from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import os
import re
import logging
import time

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Max file 10MB

# Ganti summarizer besar dengan sentence-transformers ringan
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
kw_model = KeyBERT(model=embedding_model)

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_references(text):
    return re.sub(r'(References|Bibliography|Daftar Pustaka)(.*)', '', text, flags=re.DOTALL)

def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                logging.info(f"Teks ditemukan pada halaman {i+1}")
                text += page_text + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return None

@app.route("/", methods=["GET"])
def home():
    return "Smart Document Analyzer API is running. Please send a POST request to /analyze with a PDF file."

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".pdf"):
        return jsonify({"error": "File tidak valid. Harus PDF."}), 400

    try:
        text = extract_text_from_pdf(file)
        if not text:
            return jsonify({"error": "Tidak ada teks yang dapat diekstrak dari PDF."}), 400

        text = clean_text(remove_references(text))

        processing_time = round(time.time(), 2)

        try:
            keywords = kw_model.extract_keywords(text, top_n=5)
            highlights = [kw[0].capitalize() for kw in keywords if len(kw[0].split()) <= 4]
        except Exception as e:
            logging.warning(f"Gagal mengekstrak keyword: {e}")
            highlights = list(set(text.split()[:5]))

        return jsonify({
            "summary": "(Ringkasan tidak tersedia di versi ringan)",
            "highlights": highlights,
            "processing_time": processing_time,
        })

    except Exception as e:
        logging.error(f"Kesalahan server: {e}")
        return jsonify({"error": f"Gagal memproses file: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)
