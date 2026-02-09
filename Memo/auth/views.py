import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from models import db, User
from forms import LoginForm, SignUpForm, EditUserForm
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
from utils.upload import save_upload
from dotenv import load_dotenv
load_dotenv()

# 第一引数がurl_for、第三引数がrender_templateで使用する接頭辞
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ログイン
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    # ログイン済みならマイページにリダイレクト
    if current_user.is_authenticated:
        return redirect(url_for('memo.index'))

    form = LoginForm()

    # 入力値判定とユーザー情報の取得
    if form.validate_on_submit():
        # メールアドレスを空白削除小文字に変換して1件分のユーザー情報を取得
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        # ユーザー情報とパスワードの認証チェック通常ログイン判定
        if not user or not (user.password and check_password_hash(user.password, form.password.data)):
            # エラーメッセージはセキュリティ上どちらが原因かを限定表示しない
            flash('メールアドレスまたはパスワードが正しくありません', 'danger')
            return render_template('auth/login.j2', form=form)

        # OAuth専用ユーザーのブロック
        if user.oauth_provider:
            flash('このアカウントはGoogleログイン専用です', 'secondary')
            return render_template('auth/login.j2', form=form)

        # ログイン完了
        login_user(user, remember=form.remember.data)
        flash('ログインしました', 'secondary')
        return redirect(url_for('memo.index'))

    return render_template('auth/login.j2', form=form)

# サインアップ
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
  form = SignUpForm() # 登録フォームクラスの読み込み
  if form.validate_on_submit():
    username = form.username.data
    email = form.email.data.strip().lower()
    password = form.password.data
    user =  User(
      username=username,
      email=email,
      password=generate_password_hash(form.password.data)
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash('ユーザ登録が完了しました', 'secondary')
    return redirect(url_for('auth.login'))
  return render_template('auth/register.j2', form=form)

# ログアウト
@auth_bp.route('/logout')
@login_required
def logout():
    # ログアウト状態に変換
    logout_user()
    flash('ログアウトしました', 'secondary')
    return redirect(url_for('auth.login'))

# サムネイル一覧の用意
USER_THUMBNAILS = [f"{i:02}.png" for i in range(1, 11)]

# ユーザー編集
@auth_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditUserForm(obj=current_user)
    if request.method == 'POST' and form.validate_on_submit():
        # ユーザー名更新
        if not current_user.is_oauth_user:
            current_user.username = form.username.data
        # パスワード更新
        if not current_user.is_oauth_user and form.change_password.data:
            current_user.set_password(form.password.data)
        # ファイルアップロード優先
        if form.thumbnail.data:
            file = form.thumbnail.data
            filename = save_upload(file, 'user')
            current_user.thumbnail = filename
        # ファイルが無ければプリセット
        elif form.preset_thumbnail.data:
            current_user.thumbnail = form.preset_thumbnail.data
        db.session.commit()
        flash('ユーザー情報を更新しました', 'secondary')
        return redirect(url_for('auth.edit'))
    return render_template(
        'auth/edit.j2',
        form=form,
        email=current_user.email,
        thumbnails=USER_THUMBNAILS
    )

# ユーザー削除
@auth_bp.route('/delete', methods=['POST'])
@login_required
def delete():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('ユーザー情報を削除しました', 'secondary')
    return redirect(url_for('public.public_index'))

# Google OAuth
oauth = OAuth(current_app)
oauth.register(
    name='google',
    client_id=os.environ['GOOGLE_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Googleへのリダイレクト(URIはGoogleの設定とFlask側が一致していないとエラー)
@auth_bp.route('/oauth_login')
def oauth_login():
    redirect_uri = url_for('auth.auth_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def auth_callback():
    # token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()
    session['oauth_user'] = user_info
    return redirect(url_for('auth.login'))

# Googleが返すオブジェクトを基にアクセストークンとユーザー情報を取得
@auth_bp.route('/google/callback')
def auth_google():
    # token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()

    oauth_sub = user_info['id']
    email = user_info['email']
    name = user_info['name']

    user = User.query.filter_by(
        oauth_provider='google',
        oauth_sub=oauth_sub
    ).first()

    if not user:
        user = User(
            username=name,
            email=email,
            oauth_provider='google',
            oauth_sub=oauth_sub
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Googleログインが成功しました', 'secondary')
    return redirect(url_for('memo.index'))
