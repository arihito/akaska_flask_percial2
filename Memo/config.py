import os
from datetime import timedelta
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG=True
    SECRET_KEY = 'secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/memodb.sqlite'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images/memo")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB 制限（任意）
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=30) # ログイン状態の保持期間
    