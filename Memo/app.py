from flask import Flask
from flask_migrate import Migrate
from models import db, User
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
# Blueprints
from public.views import public_bp
from auth.views import auth_bp
from memo.views import memo_bp
from favorite.views import favorite_bp
from fixed.views import fixed_bp, STATIC_PAGES
from errors.views import error_bp

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
toolbar = DebugToolbarExtension(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app) # Flaskアプリに紐付け
# アクセス制限ページからリダイレクト後のflashメッセージ
login_manager.login_message = '認証していません：ログインしてください'
login_manager.login_view = 'auth.login' # 不正アクセスはログインページへ
app.register_blueprint(public_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(memo_bp)
app.register_blueprint(favorite_bp)
app.register_blueprint(fixed_bp)
app.register_blueprint(error_bp)

# 全テンプレートに値を共有
@app.context_processor
def inject_static_pages():
    return dict(STATIC_PAGES=STATIC_PAGES)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# if __name__ == '__main__':
#     app.run()
