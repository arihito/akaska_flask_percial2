from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Flask-SQLAlchemyの生成
db = SQLAlchemy()

# モデル

# ユーザー
class User(db.Model, UserMixin):
    # テーブル名
    __tablename__ = 'users'
    # ID(PK)
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # ユーザー名
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    # メールアドレス
    email = db.Column(db.String(50), unique=True, nullable=False)
    # パスワード
    password = db.Column(db.String(255), nullable=False)
    # 管理者権限の有無
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    # 有効ユーザーの判別
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # 登録日
    registration_date = db.Column(db.DateTime, server_default=db.func.now())

    def get_id(self):
        return self.user_id
    # パスワードをハッシュ化して設定する
    def set_password(self, password):
        self.password = generate_password_hash(password)
    # 入力したパスワードとハッシュ化されたパスワードの比較
    def check_password(self, password):
        return check_password_hash(self.password, password)

# レビュー
class Review(db.Model):
    # テーブル名
    __tablename__ = 'reviews'
    # ID(PK)
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # プロダクトID
    product_id = db.Column(db.String(50), nullable=False)
    # 評価値
    score = db.Column(db.Integer)
    # 自由記述欄
    free_comment = db.Column(db.Text)
    # 登録日
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

# 製品管理
class Product(db.Model):
    # テーブル名
    __tablename__ = 'products'
    # ID(PK)
    product_id = db.Column(db.Integer, primary_key=True)
    # 製品名
    product_name = db.Column(db.String(50), nullable=False)
    # 価格
    price = db.Column(db.Integer, nullable=False)
    # 発売日
    released_date = db.Column(db.DateTime, nullable=False)
    
    # def get_id(self):
    #     return self.product_id