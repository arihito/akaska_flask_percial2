import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # デバッグ(開発)モード
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'

    # セッション・CSRF対策
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # SQLパフォーマンス
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ログ制御
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', '0') == '1'

    # マルチDBアクセスパス
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "instance", "memodb.sqlite")}'
    )

    # 投稿用アップロードフォルダパス
    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        os.getenv('UPLOAD_FOLDER', 'static/images/memo')
    )

    # ファイルアップロード最大サイズ
    MAX_CONTENT_LENGTH = int(
        os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)
    )

    # ファイルフォーマット
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # 開発ツール使用時のログインリダイレクト一時停止
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # ログイン状態の保持期間日数
    REMEMBER_COOKIE_DURATION = timedelta(
        days=int(os.getenv('REMEMBER_DAYS', 7))
    )
    
    # Googleログイン
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'xxxxxx')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'xxxxxx')
