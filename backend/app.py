import os
import uuid
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from flask_cors import CORS

from sorting import rank_resumes

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "resume-uploads")

ALLOWED_EXTENSIONS = {"pdf", "docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream"  # some browsers lie about DOCX
}

app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File too large. Max size is 5MB."}), 413

@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF and DOCX files are allowed"}), 400

    if file.mimetype not in ALLOWED_MIME_TYPES:
        return jsonify({"error": "Invalid file type"}), 400

    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid.uuid4()}.{ext}"

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)
    file.save(save_path)

    return jsonify({
        "message": "File uploaded successfully",
        "original_filename": original_filename,
        "stored_filename": stored_filename
    }), 201

@app.route("/matcher", methods=["POST"])
def matcher():
    job_description = request.form.get("job_description")

    if not job_description:
        return jsonify({"error": "Job description is required"}), 400

    if "resumes" not in request.files:
        return jsonify({"error": "No resumes uploaded"}), 400

    files = request.files.getlist("resumes")

    if not files:
        return jsonify({"error": "Please upload at least one resume"}), 400

    saved_files = []

    filename_map = {}

    for file in files:
        if file.filename == "":
            continue

        if not allowed_file(file.filename):
            return jsonify({"error": f"Invalid file type: {file.filename}"}), 400

        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit(".", 1)[1].lower()
        stored_filename = f"{uuid.uuid4()}.{ext}"

        save_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_filename)
        file.save(save_path)

        filename_map[stored_filename] = original_filename

        saved_files.append({
            "original_filename": original_filename,
            "stored_filename": stored_filename
        })

    results = rank_resumes(job_description)

    rankings = [
        {
            "filename": filename_map.get(stored, stored),
            "score": float(score)
        }
        for stored, score in results
    ]

    return jsonify({
        "message": "Resumes processed and ranked",
        "rankings": rankings
    }), 200

if __name__ == "__main__":
    app.run(debug=True)