from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import pytz

db = SQLAlchemy()

memo_categories = db.Table(
    "memo_categories",
    db.Column("memo_id", db.Integer, db.ForeignKey("memos.id",  ondelete="CASCADE"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
)

class Memo(db.Model):
    __tablename__ = 'memos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_memos_users'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    image_filename = db.Column(db.String(255), nullable=False, default="nofile.jpg")
    user = relationship('User', back_populates='memos')
    favorites = relationship('Favorite', back_populates='memo', cascade="all, delete-orphan")
    categories = relationship("Category", secondary=memo_categories, back_populates="memos")

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    memos = relationship("Memo", secondary=memo_categories, back_populates="categories")

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_favorites_users'), nullable=False)
    memo_id = db.Column(db.Integer, db.ForeignKey('memos.id', name='fk_favorites_memos'), nullable=False)
    rank = db.Column(db.Integer, nullable=True)  # ランク（1〜5想定、NULLは未ランク）
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    user = relationship('User', back_populates='favorites')
    memo = relationship('Memo', back_populates='favorites')
    __table_args__ = (db.UniqueConstraint('user_id', 'memo_id', name='uq_user_memo_favorite'),)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(12), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=True)
    thumbnail = db.Column(db.String(50), nullable=False, default='default.png')
    oauth_provider = db.Column(db.String(50)) # 'google'
    oauth_sub = db.Column(db.String(255)) # Googleのsub/id
    # 管理者関連
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_paid = db.Column(db.Boolean, nullable=False, default=False)
    admin_password = db.Column(db.String(120), nullable=True)
    subscription_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    memos = relationship('Memo', back_populates='user')
    favorites = relationship('Favorite', back_populates='user', cascade="all, delete-orphan")
    @property
    def is_oauth_user(self):
        return self.oauth_provider is not None
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        if not self.password:
            return False
        return check_password_hash(self.password, password)
    def set_admin_password(self, password):
        self.admin_password = generate_password_hash(password)
    def check_admin_password(self, password):
        if not self.admin_password:
            return False
        return check_password_hash(self.admin_password, password)

