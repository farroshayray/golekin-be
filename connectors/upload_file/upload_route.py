from . import upload_file
from flask import Flask, current_app, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import url_for

def save_file(file):
    if not file:
        raise ValueError("No file provided")
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure folder exists
    file.save(file_path)
    # Generate absolute URL
    return url_for("upload_file.uploaded_files", filename=filename, _external=True)


@upload_file.route("/")
def test_upload_file():
    return "<div>Upload File</div>"

@upload_file.route("/files", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    try:
        file_url = save_file(file)
        return jsonify({"url": file_url}), 201  # Use 201 for resource creation
    except ValueError as e:
        return jsonify({"error": str(e)}), 415  # Unsupported Media Type
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@upload_file.route("/uploaded_files/<filename>")
def uploaded_files(filename):
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

