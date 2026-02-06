import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from models import db, User
from forms import LoginForm, SignUpForm, EditUserForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
load_dotenv()

# 第一引数がurl_for、第三引数がrender_templateで使用する接頭辞
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('memo.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            flash('ユーザー名またはパスワードが正しくありません', 'danger')
            return render_template('auth/login.j2', form=form)

        # OAuth専用ユーザーのブロック
        if user.oauth_provider:
            flash('このアカウントはGoogleログイン専用です', 'warning')
            return render_template('auth/login.j2', form=form)

        # 通常ログイン
        if not user.check_password(form.password.data):
            flash('ユーザー名またはパスワードが正しくありません', 'danger')
            return render_template('auth/login.j2', form=form)

        login_user(user, remember=form.remember.data)
        flash('ログインしました', 'success')
        return redirect(url_for('memo.index'))

    return render_template('auth/login.j2', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # ログアウト状態に変換
    logout_user()
    flash('ログアウトしました')
    return redirect(url_for('auth.login'))
	
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
	form = SignUpForm() # 登録フォームクラスの読み込み
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		user = User(username=username)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		flash('ユーザ登録しました')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.j2', form=form)

# サムネイル一覧の用意
USER_THUMBNAILS = [f"{i:02}.png" for i in range(1, 11)]

@auth_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditUserForm(obj=current_user)  # ← 既存値を初期表示
    if request.method == 'POST':
        if form.username.data != current_user.username:
            exists = User.query.filter_by(username=form.username.data).first()
            if exists:
                form.username.errors.append('このユーザー名は既に使用されています')
        if form.validate_on_submit():
            # ユーザー名更新
            current_user.username = form.username.data
            # 入力があった場合のみパスワード更新
            if form.change_password.data:
                current_user.set_password(form.password.data)
            # アップロードされた場合のみサムネイル画像保存
            # サムネイル更新
            if form.thumbnail.data:  # ファイルアップロード優先
                file = form.thumbnail.data
                filename = secure_filename(file.filename)
                print("更新前の current_user.thumbnail =", current_user.thumbnail)
                print("アップロードされるファイル名 =", filename)
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, filename)
                file.save(save_path)
                current_user.thumbnail = filename
            elif form.preset_thumbnail.data:  # ファイルがなければラジオ選択
                print("更新前の current_user.thumbnail =", current_user.thumbnail)
                print("選択された preset_thumbnail =", form.preset_thumbnail.data)
                current_user.thumbnail = form.preset_thumbnail.data
            db.session.commit()
            flash('ユーザー情報を更新しました', 'success')
            return redirect(url_for('auth.edit'))
    return render_template('auth/edit.j2', form=form, email=current_user.email, thumbnails=USER_THUMBNAILS)

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
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()
    session['oauth_user'] = user_info
    return redirect(url_for('auth.login'))

# Googleが返すオブジェクトを基にアクセストークンとユーザー情報を取得
@auth_bp.route('/google/callback')
def auth_google():
    token = oauth.google.authorize_access_token()
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
    flash('Googleでログインしました', 'success')
    return redirect(url_for('memo.index'))
