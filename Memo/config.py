import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG=True
    SECRET_KEY = 'secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///memodb.sqlite'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images/memo")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB 制限（任意）
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    
    