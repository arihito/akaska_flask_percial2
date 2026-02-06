import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def save_upload(file, category: str) -> str:
    if not file or file.filename == '':
        return None
    original = secure_filename(file.filename)
    ext = os.path.splitext(original)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(
        current_app.root_path,
        'static',
        'images',
        category
    )
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)
    return filename
