from flask import Flask
from flask_migrate import Migrate
from models import db, User, FixedPage
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import NotFound, InternalServerError
from errors.views import show_404_page
from utils.logger import init_logger
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

from public.views import public_bp
from auth.views import auth_bp
from memo.views import memo_bp
from favorite.views import favorite_bp
from docs.views import docs_bp
from fixed.views import fixed_bp
from admin.views import admin_bp
from admin.webhook import webhook_bp

import stripe
from flask_mail import Mail
from dotenv import load_dotenv
load_dotenv()


# SQLite の FOREIGN KEY 制約を有効化（モジュールレベルで一度だけ登録）
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(config_override=None):
    """アプリケーションファクトリ。config_override でテスト用設定を上書き可能。"""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    if config_override:
        app.config.update(config_override)

    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    db.init_app(app)

    Mail(app)
    if not app.testing:
        DebugToolbarExtension(app)
    Migrate(app, db)
    init_logger(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_message = '認証していません：ログインしてください'
    login_manager.login_view = 'auth.login'

    app.register_error_handler(NotFound, show_404_page)

    @app.errorhandler(InternalServerError)
    def show_500_page(error):
        app.logger.error(
            'Internal Server Error: %s', str(error), exc_info=True
        )
        return '500 Internal Server Error', 500

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(memo_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(fixed_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(webhook_bp)

    @app.context_processor
    def inject_static_pages():
        try:
            pages = FixedPage.query.filter_by(visible=True).order_by(FixedPage.order).all()
            GLOBAL_NAV_PAGES = {p.key: p.title for p in pages if p.nav_type == 'global'}
            FOOTER_NAV_PAGES = {p.key: p.title for p in pages if p.nav_type == 'footer'}
        except Exception:
            GLOBAL_NAV_PAGES = {}
            FOOTER_NAV_PAGES = {}
        return dict(
            GLOBAL_NAV_PAGES=GLOBAL_NAV_PAGES,
            FOOTER_NAV_PAGES=FOOTER_NAV_PAGES,
            SITE_NAME=app.config['SITE_NAME'],
        )

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app


# モジュールレベルの後方互換（gunicorn 等が参照）
app = create_app()

if __name__ == '__main__':
    app.run()
