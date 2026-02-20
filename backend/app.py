import os
import uuid
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream"
}

app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 *1024

os.makedirs(UPLOAD_FOLDER, exist_ok = True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/upload-resume", methods = ["POST"])
def upload_resume():
    if "file" not in request.files:
        return jsonify({"Error": "No file part in request"}), 400
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"Error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"Error": "Only PDF and DOCX files are allowed"}), 400
    
    if file.mimetype not in ALLOWED_MIME_TYPES:
        return jsonify({"Error": "Invalid file type"}), 400
    
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid.uuid4()}.{ext}"

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)
    file.save(save_path)

    return jsonify({
        "Message": "File uploaded successfully", 
        "Original filename": original_filename,
        "Stored filename": stored_filename
        }), 201

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"Error": "File too large. Max size is 5MB."}), 413

if __name__ == "__main__":
    app.run(debug = True)