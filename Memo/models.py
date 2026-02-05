from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

db = SQLAlchemy()

class Memo(db.Model):
    __tablename__ = 'memos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_memos_users'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Tokyo')))
    user = relationship('User', back_populates='memos')
    favorites = relationship('Favorite', back_populates='memo', cascade="all, delete-orphan")
    image_filename = db.Column(db.String(255), nullable=False, default="nofile.jpg")

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_favorites_users'), nullable=False)
    memo_id = db.Column(db.Integer, db.ForeignKey('memos.id', name='fk_favorites_memos'), nullable=False)
    rank = db.Column(db.Integer, nullable=True)  # ランク（1〜5想定、NULLは未ランク）
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Tokyo')))
    user = relationship('User', back_populates='favorites')
    memo = relationship('Memo', back_populates='favorites')
    __table_args__ = (db.UniqueConstraint('user_id', 'memo_id', name='uq_user_memo_favorite'),)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=False)
    thumbnail = db.Column(db.String(50), nullable=False, default='default.png')
    memos = relationship('Memo', back_populates='user')
    favorites = relationship('Favorite', back_populates='user', cascade="all, delete-orphan")
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
