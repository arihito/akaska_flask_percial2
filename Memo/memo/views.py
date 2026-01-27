import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, Memo, User, Favorite
from flask_login import login_required, current_user
from forms import MemoForm
from sqlalchemy import func
from werkzeug.utils import secure_filename
import uuid

# 第一引数がurl_for、第三引数がrender_templateで使用する接頭辞
memo_bp = Blueprint('memo', __name__, url_prefix='/memo')

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )

@memo_bp.route('/')
@login_required
def index():
    WEEKDAYS_JA = ['月', '火', '水', '木', '金', '土', '日']
    raw_memos = (
        db.session.query(Memo, func.count(Favorite.id).label("like_count"))
            .outerjoin(Favorite, Memo.id == Favorite.memo_id)
            .filter(Memo.user_id == current_user.id)
            .group_by(Memo.id)
            .all()
    )
    memos = []
    for memo, like_count in raw_memos:
        memo.weekday_ja = WEEKDAYS_JA[memo.created_at.weekday()]
        memos.append({
            "memo": memo,
            "like_count": like_count
        })
    top5 = (Favorite.query.filter_by(user_id=current_user.id).filter(Favorite.rank != None).order_by(Favorite.rank.asc()).limit(5).all())
    return render_template('memo/index.j2', memos=memos, top5=top5, user=current_user)

@memo_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = MemoForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = "nofile.jpg"
        if image_file and allowed_file(image_file.filename):
            original = secure_filename(image_file.filename)
            ext = original.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            image_file.save(save_path)
        memo = Memo(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            image_filename=filename
        )
        db.session.add(memo)
        db.session.commit()
        flash('登録しました')
        return redirect(url_for('memo.index'))
    return render_template('memo/create.j2', form=form)

@memo_bp.route('/update/<int:memo_id>', methods=['GET', 'POST'])
@login_required
def update(memo_id):
    memo = Memo.query.filter_by(id=memo_id, user_id=current_user.id).first_or_404()
    form = MemoForm(obj=memo)  # 既存データをフォームに流し込む
    if form.validate_on_submit():
        memo.title = request.form['title']
        memo.content = request.form['content']
        image_file = form.image.data
        if image_file and allowed_file(image_file.filename):
            original = secure_filename(image_file.filename)
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], original)
            # 同名ファイルはそのまま上書き保存される
            image_file.save(save_path)
            memo.image_filename = original
        db.session.commit()
        flash('変更しました')
        return redirect(url_for('memo.index'))
    return render_template('memo/update.j2', memo=memo, form=form)

@memo_bp.route('/delete/<int:memo_id>')
@login_required
def delete(memo_id):
    memo = Memo.query.filter_by(id=memo_id, user_id=current_user.id).first_or_404()
    db.session.delete(memo)
    db.session.commit()
    flash('削除しました')
    return redirect(url_for('memo.index'))