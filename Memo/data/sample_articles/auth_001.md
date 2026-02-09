# Flask-Loginによる認証機能の実装

## Flask-Loginとは

Flask-Loginは、ユーザー認証とセッション管理を簡単に実装できるFlask拡張機能です。ログイン、ログアウト、ログイン状態の保持、アクセス制御などを簡潔なコードで実現できます。

## セットアップ

### インストール
```bash
pip install Flask-Login
```

### 初期化
```python
# app.py
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # 未ログイン時のリダイレクト先
login_manager.login_message = 'ログインが必要です'
```

## Userモデルの実装

Flask-Loginを使うには、UserモデルがUserMixinを継承する必要があります。

```python
# models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        """パスワードをハッシュ化して保存"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """パスワードの検証"""
        return check_password_hash(self.password, password)
```

## ユーザーローダーの設定

Flask-Loginがセッションからユーザーを取得するためのコールバック関数を定義します。

```python
# app.py
from flask_login import LoginManager
from models import User

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

## ログイン機能の実装

### ログインフォーム
```python
# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    remember = BooleanField('ログイン状態を保持')
    submit = SubmitField('ログイン')
```

### ログインビュー
```python
# auth/views.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, current_user
from models import User
from forms import LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 既にログイン済みの場合はリダイレクト
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # ユーザー存在確認とパスワード検証
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('ログインしました', 'success')
            
            # next パラメータがあればそこにリダイレクト
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('メールアドレスまたはパスワードが間違っています', 'danger')
    
    return render_template('auth/login.html', form=form)
```

## ログアウト機能

```python
from flask_login import logout_user

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('ログアウトしました', 'info')
    return redirect(url_for('index'))
```

## アクセス制御

### @login_requiredデコレータ
```python
from flask_login import login_required, current_user

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
```

### カスタム権限チェック
```python
from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin/index.html')
```

## ユーザー登録機能

```python
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)
```

## テンプレートでの使用

```html
{% if current_user.is_authenticated %}
    <p>ようこそ、{{ current_user.username }}さん</p>
    <a href="{{ url_for('auth.logout') }}">ログアウト</a>
{% else %}
    <a href="{{ url_for('auth.login') }}">ログイン</a>
    <a href="{{ url_for('auth.register') }}">新規登録</a>
{% endif %}
```

## セッション設定のカスタマイズ

```python
# config.py
from datetime import timedelta

class Config:
    # セッションの有効期限
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # セッションクッキーの設定
    SESSION_COOKIE_SECURE = True  # HTTPS接続時のみ
    SESSION_COOKIE_HTTPONLY = True  # JavaScriptからのアクセス防止
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF対策
```

## まとめ

Flask-Loginを使うことで、複雑な認証ロジックを簡潔に実装できます。UserMixinの継承、user_loaderの設定、@login_requiredデコレータの3つのポイントを押さえれば、堅牢な認証システムを構築できます。セキュリティ面では、パスワードのハッシュ化とHTTPS通信が必須です。
