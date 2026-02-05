from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, User
from forms import LoginForm, SignUpForm, EditUserForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os

# 第一引数がurl_for、第三引数がrender_templateで使用する接頭辞
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('memo.index'))
    form = LoginForm() # ログインフォームクラスの読み込み
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('ログインしました', 'success')
            return redirect(url_for('memo.index'))
        else:
            flash('ユーザー名またはパスワードが正しくありません', 'danger')
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
        # デバッグプリント：フォーム送信確認
        print("######################## POST request detected")
        print("######################## form.validate_on_submit() =", form.validate_on_submit())
        print("######################## form.thumbnail.data =", form.thumbnail.data)
        print("######################## form.preset_thumbnail.data =", form.preset_thumbnail.data)
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
    return render_template('auth/edit.j2', form=form, thumbnails=USER_THUMBNAILS)
