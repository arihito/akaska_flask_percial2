import os
from flask import Flask, request, render_template, jsonify
from pathlib import Path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

IMAGE_DIR = Path("static/images")
ALLOWED_SUFFIXES = {".jpg", ".png"}

def get_images():
    return sorted(
      (
          p.relative_to("static").as_posix()
          for p in IMAGE_DIR.iterdir()
          if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES
      ),
      reverse=True
    )

@app.route("/")
def index():
    return render_template("upload.j2", images=get_images())

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":
      if "file" not in request.files:
          return jsonify({"error": "No file part"}), 400

      file = request.files["file"]

      if file.filename == "":
          return jsonify({"error": "ファイルを選択できませんでした"}), 400

      # 保存先パス作成
      save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
      file.save(save_path)

      return jsonify({"success": True, "filename": file.filename})
    return render_template("upload.j2", images=get_images())

if __name__ == "__main__":
    app.run(debug=True)
