from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from flask_cors import CORS

# Configuración de Flask
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"pdf", "tiff", "tif"}  # Corregido
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Configurar rutas de ejecutables
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
poppler_path = r"C:\\Users\\aalvarez\\Documents\\poppler-24.08.0\\Library\\bin"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/extract-text", methods=["POST"])
def extract_text():
    if "file" not in request.files:
        return jsonify({"error": "No se proporcionó ningún archivo."}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Formato de archivo no permitido."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    extracted_text = ""

    # Procesar PDFs
    if filename.lower().endswith(".pdf"):
        images = convert_from_path(filepath, poppler_path=poppler_path)
        for image in images:
            extracted_text += pytesseract.image_to_string(image) + "\n"
    
    # Procesar imágenes TIFF/TIF
    else:
        image = Image.open(filepath)
        extracted_text = pytesseract.image_to_string(image)

    os.remove(filepath)  # Eliminar el archivo tras el procesamiento
    return jsonify({"text": extracted_text.strip()})

if __name__ == "__main__":
    app.run(debug=True)
