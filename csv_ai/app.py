from flask import Flask,render_template
from flask_migrate import Migrate
from models import db, User
from flask_login import LoginManager
from auth.views import auth_bp
from product.views import product_bp

# Flask
app = Flask(__name__)
# 設定ファイル読み込み
app.config.from_object("config.Config")
# dbとFlaskの紐づけ
db.init_app(app)
# マイグレーションとの紐づけ(Flaskとdb)
migrate = Migrate(app, db)
# LoginManagerインスタンス
login_manager = LoginManager()
# LoginManagerとFlaskとの紐づけ
login_manager.init_app(app)
# メッセージ変更
login_manager.login_message = "認証していません：ログインしてください"
# 未認証のユーザーがアクセスしようとした際にリダイレクトされる関数を設定
login_manager.login_view = "auth.login"
# blueprintをアプリケーションに登録
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)

# 404エラー時の処理
@app.errorhandler(404)
def not_found(error):
    # error 変数にはエラーの情報が入る（必要なら表示可能）
    return render_template("errors/404.html", msg="ページが見つかりませんでした（404）"), 404

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 実行
if __name__ == "__main__":
    app.run()