from flask import Flask
from flask_migrate import Migrate
from models import db, User
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import NotFound
from errors.views import show_404_page

# Blueprints
from public.views import public_bp              # トップページ
from auth.views import auth_bp                  # ログイン認証
from memo.views import memo_bp                  # マイページ
from favorite.views import favorite_bp          # いいね
from docs.views import docs_bp                  # 成果物
from fixed.views import fixed_bp, STATIC_PAGES  # 固定ページ
from admin.views import admin_bp                # 管理者
from admin.webhook import webhook_bp            # Stripe Webhook

import stripe
from flask_mail import Mail
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')
stripe.api_key = app.config['STRIPE_SECRET_KEY']
db.init_app(app)
mail = Mail(app)
toolbar = DebugToolbarExtension(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app) # Flaskアプリに紐付け
# アクセス制限ページからリダイレクト後のflashメッセージ
login_manager.login_message = '認証していません：ログインしてください'
login_manager.login_view = 'auth.login' # 不正アクセスはログインページへ
app.register_error_handler(NotFound, show_404_page)
app.register_blueprint(public_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(memo_bp)
app.register_blueprint(favorite_bp)
app.register_blueprint(docs_bp)
app.register_blueprint(fixed_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(webhook_bp)

# 全テンプレートに値を共有
@app.context_processor
def inject_static_pages():
    return dict(
        STATIC_PAGES=STATIC_PAGES,
        SITE_NAME=app.config['SITE_NAME'],
    )

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run()
