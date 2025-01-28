from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import pdfplumber
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Crear carpeta de subidas si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    """Extrae el texto de un archivo PDF utilizando pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  # Verifica si hay texto en la página
                    text += page_text + "\n"
        return text
    except Exception as e:
        return str(e)

@app.route("/extract-text", methods=["POST"])
def extract_text():
    # Verificar si el archivo está en la solicitud
    if "file" not in request.files:
        return jsonify({"error": "No se proporcionó ningún archivo."}), 400

    file = request.files["file"]

    # Verificar si el archivo tiene un nombre y es un PDF válido
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Por favor sube un archivo PDF válido."}), 400

    # Guardar el archivo de manera segura
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Extraer texto del archivo PDF
    extracted_text = extract_text_from_pdf(filepath)

    # Eliminar el archivo después de procesarlo
    os.remove(filepath)

    return jsonify({"text": extracted_text})

if __name__ == "__main__":
    app.run(debug=True)
