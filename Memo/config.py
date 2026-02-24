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
    UPLOAD_FOLDERS = {
        'memo': 'static/images/memo',
        'user': 'static/images/user',
    }

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

    # Stripe決済
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    ADMIN_PLAN_PRICE = 480       # 管理者プラン料金（円）
    ADMIN_PLAN_HOURS = 24        # 管理者プラン有効時間
    ADMIN_PLAN_POINTS = 24       # 決済ごとに付与するポイント数

    # サイト名
    SITE_NAME = os.getenv('SITE_NAME', 'Flask tech blog')

    # メール送信（Gmail SMTP）
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', '')

    # Gemini AI API
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
