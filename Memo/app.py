from flask import Flask, send_from_directory, request
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

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/x-icon')

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(memo_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(fixed_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(webhook_bp)

    _EN_LABELS = {
        'login': 'Sign In',
        'register': 'Register',
        'logout': 'Sign Out',
        'top': 'Top',
        'today_pick': "Today's Pick",
        'today_pick_sub': 'Article changes randomly once a day',
        'recommended': 'Recommended for You',
        'recommended_sub': 'Articles recommended based on your post categories',
        'posted_by': 'Posted by:',
        'posted_on': 'Posted on:',
        'likes': 'Likes',
        'back_to_top': 'Back to Top',
        'back_prev': 'Previous Page',
        'back_list': 'Back to List',
        'login_prompt': 'Sign in to like!',
        'own_article': 'Your article',
        'ranking_title': 'Top 10 Most Liked',
        'ranking_sub': 'Top 10 articles ranked by number of likes.',
        'footer_desc': (
            'This Flask tech blog was created for the purpose of learning Flask '
            'application development as a vocational training assignment.'
        ),
    }

    @app.context_processor
    def inject_global_context():
        try:
            pages = FixedPage.query.filter_by(visible=True).order_by(FixedPage.order).all()
            GLOBAL_NAV_PAGES    = {p.key: p.title for p in pages if p.nav_type == 'global'}
            FOOTER_NAV_PAGES    = {p.key: p.title for p in pages if p.nav_type == 'footer'}
            EN_GLOBAL_NAV_PAGES = {p.key: (p.en_title or p.title) for p in pages if p.nav_type == 'global'}
            EN_FOOTER_NAV_PAGES = {p.key: (p.en_title or p.title) for p in pages if p.nav_type == 'footer'}
        except Exception as e:
            app.logger.warning("inject_global_context: DB取得失敗 %s", e)
            GLOBAL_NAV_PAGES = FOOTER_NAV_PAGES = {}
            EN_GLOBAL_NAV_PAGES = EN_FOOTER_NAV_PAGES = {}

        # 英語ページ判定
        is_english = request.path.startswith('/en')

        # 言語切替URL（/en/detail/1 → /detail/1、/detail/1 → /en/detail/1）
        path = request.path
        if path.startswith('/en'):
            lang_switch_url = path[3:] or '/'
        else:
            lang_switch_url = '/en' + path

        return dict(
            GLOBAL_NAV_PAGES=GLOBAL_NAV_PAGES,
            FOOTER_NAV_PAGES=FOOTER_NAV_PAGES,
            EN_GLOBAL_NAV_PAGES=EN_GLOBAL_NAV_PAGES,
            EN_FOOTER_NAV_PAGES=EN_FOOTER_NAV_PAGES,
            SITE_NAME=app.config['SITE_NAME'],
            is_english=is_english,
            lang_switch_url=lang_switch_url,
            EN_LABELS=_EN_LABELS,
        )

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ResendのSPF通信テスト
    from flask import jsonify
    from utils.mail import send_test_email
    # テスト実行用のURL
    @app.route("/debug/resend")
    def debug_resend_route():
        # ご自身の受信可能なメールアドレスを指定
        success, result = send_test_email("arihito.m@gmail.com")
        if success:
            return jsonify({"status": "success", "data": result})
        else:
            return jsonify({"status": "error", "message": result}), 500

    return app


# モジュールレベルの後方互換（gunicorn 等が参照）
app = create_app()


@app.cli.command('translate-memos')
def translate_memos_command():
    """ai_score 付き・未翻訳の Memo を全件 Gemini で英語翻訳して DB に保存する。"""
    from models import Memo
    from utils.ai_translate import translate_memo_to_english
    import time

    targets = [m for m in Memo.query.all()
               if m.ai_score and not m.ai_score.get('translated_title')]

    if not targets:
        print('翻訳対象なし（全件翻訳済みか ai_score 未評価）')
        return

    print(f'翻訳対象: {len(targets)} 件')
    ok = ng = 0
    for memo in targets:
        print(f'  [{memo.id}] {memo.title[:40]} ... ', end='', flush=True)
        result = translate_memo_to_english(memo.title, memo.content)
        if result:
            updated = dict(memo.ai_score)
            updated['translated_title'] = result['translated_title']
            updated['translated_body']  = result['translated_body']
            memo.ai_score = updated
            db.session.commit()
            print('OK')
            ok += 1
        else:
            print('FAIL')
            ng += 1
        time.sleep(1)  # レートリミット対策

    print(f'\n完了: 成功 {ok} 件 / 失敗 {ng} 件')


if __name__ == '__main__':
    app.run()
