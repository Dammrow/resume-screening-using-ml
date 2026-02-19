import os
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok = True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/upload-resume", methods = ["POST"])
def upload_resume():
    if "file" not in request.files:
        return jsonify({"Error": "No file part in request"}),400
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"Error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"Error": "Only .pdf files are allowed"}), 400
    
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    return jsonify({"Message": "File uploaded successfully", "filename": filename})

if __name__ == "__main__":
    app.run(debug = True)