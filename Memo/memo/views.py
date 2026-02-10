import os
import math
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from models import db, Memo, Favorite, Category
from flask_login import login_required, current_user
from forms import MemoForm
from sqlalchemy import func, asc, desc, or_
from markupsafe import Markup, escape
from werkzeug.utils import secure_filename
from utils.upload import save_upload
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
    print(f'================================{dict(request.args)}')
    WEEKDAYS_JA = ['月', '火', '水', '木', '金', '土', '日']
    per_page = 10
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    categories = Category.query.order_by(Category.name).all()
    category_id = request.args.get('category_id', type=int)
    params = request.args.to_dict()
    # ---- 「base_query」条件の上積み ---- 
    base_query = (db.session.query(Memo, func.count(Favorite.id).label("like_count")).outerjoin(Favorite, Memo.id == Favorite.memo_id).filter(Memo.user_id == current_user.id))
    # ---- 総件数（ページ数算出用）----
    total = base_query.group_by(Memo.id).count()
    pages = math.ceil(total / per_page)
    offset = (page - 1) * per_page
    is_paginate = pages > 1
    # ---- 検索条件 ----
    if q:
        like_expr = f"%{q}%"
        base_query = base_query.filter(or_(Memo.title.ilike(like_expr),Memo.content.ilike(like_expr)))
    # ---- カテゴリー条件 ----
    if category_id:
        base_query = (base_query.join(Memo.categories).filter(Category.id == category_id))

    order = request.args.get('order', 'desc')   # 日付用
    likes = request.args.get('likes', None)     # いいね用（優先）
    # ---- いいね順の決定 ----
    if likes == 'asc':
        order_by_clause = asc(func.count(Favorite.id))
    elif likes == 'desc':
        order_by_clause = desc(func.count(Favorite.id))
    else:
        # ---- いいね順がない場合は日付順 ---- 
        order_by_clause = asc(Memo.created_at) if order == 'asc' else desc(Memo.created_at)
    #  ---- 「raw_querey」表示用の確定データ取得 ---- 
    raw_query = (
    db.session.query(Memo, func.count(Favorite.id).label("like_count")).outerjoin(Favorite, Memo.id == Favorite.memo_id).filter(Memo.user_id == current_user.id))
    # ---- カテゴリー条件 ----
    if category_id:
        raw_query = (raw_query.join(Memo.categories).filter(Category.id == category_id))
    raw_memos = (raw_query.group_by(Memo.id).order_by(order_by_clause).limit(per_page).offset(offset).all())
    memos = []
    for memo, like_count in raw_memos:
        memo.weekday_ja = WEEKDAYS_JA[memo.created_at.weekday()]
        # ---- 検索ワードのマーキング処理 ----
        if q:
            safe_title = escape(memo.title)         # タイトルをMarkup型にサニタイズ
            safe_q = escape(q)                      # 検索ワードもサニタイズ
            marked = safe_title.replace(
                safe_q,
                Markup(f"<mark>{safe_q}</mark>")    # マーカ要素を付与したHTMLを挿入
            )
            memo.marked_title = Markup(marked)      # 本文を最終的にMarkup型に変換
            safe_content = escape(memo.content)     # Markup型をサニタイズ
            safe_q = escape(q)                      # 検索ワードもサニタイズ
            marked = safe_content.replace(
                safe_q,
                Markup(f"<mark>{safe_q}</mark>")    # マーカ要素を付与したHTMLを挿入
            )
            memo.marked_content = Markup(marked)    # 最終的にMarkup型に変換
        else:
            memo.marked_title = memo.title
            memo.marked_content = memo.content

        memos.append({
            "memo": memo,
            "like_count": like_count
        })
    top5 = (Favorite.query.filter_by(user_id=current_user.id).filter(Favorite.rank != None).order_by(Favorite.rank.asc()).limit(5).all())
    return render_template(
        'memo/index.j2',
        memos=memos,
        top5=top5,
        user=current_user,
        categories=categories,
        is_paginate=is_paginate,
        params=params,
        page=page,
        pages=pages,
        total=total
    )

@memo_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = MemoForm()
    categories = Category.query.order_by(Category.name).all()
    if form.validate_on_submit():
        # ファイルアップロード
        image_file = form.image.data
        filename = "nofile.jpg"
        if image_file and allowed_file(image_file.filename):
            original = secure_filename(image_file.filename)
            # 重複禁止
            ext = original.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            upload_folder = current_app.config["UPLOAD_FOLDERS"]["memo"]
            # 目的に応じたフォルダーパスに振り分け
            save_path = os.path.join(upload_folder, filename)
            image_file.save(save_path)
        memo = Memo(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            image_filename=filename
        )
        # カテゴリー取得
        selected_ids = request.form.getlist("categories")
        if len(selected_ids) > 3:
            abort(400)
        memo.categories = Category.query.filter(Category.id.in_(selected_ids)).all()
        db.session.add(memo)
        db.session.commit()
        flash('登録しました', 'secondary')
        return redirect(url_for('memo.index'))
    return render_template('memo/create.j2', categories=categories, form=form)

@memo_bp.route('/update/<int:memo_id>', methods=['GET', 'POST'])
@login_required
def update(memo_id):
    memo = Memo.query.filter_by(id=memo_id, user_id=current_user.id).first_or_404()
    form = MemoForm(obj=memo)  # 既存データをフォームに流し込む
    categories = Category.query.order_by(Category.name).all()
    selected_category_ids = [c.id for c in memo.categories]
    if form.validate_on_submit():
        memo.title = request.form['title']
        memo.content = request.form['content']
        image_file = form.image.data
        # ファイル更新
        if image_file and allowed_file(image_file.filename):
            original = secure_filename(image_file.filename)
            filename = save_upload(original, 'memo')
            memo.image_filename = filename
        # カテゴリー更新
        selected_ids = request.form.getlist("categories")
        if len(selected_ids) > 3:
            abort(400)
        memo.categories = Category.query.filter(Category.id.in_(selected_ids)).all()
        db.session.commit()
        flash('変更しました', 'secondary')
        return redirect(url_for('memo.index'))
    return render_template(
        'memo/update.j2',
        memo=memo,
        categories=categories,
        selected_category_ids=selected_category_ids,
        form=form
    )

@memo_bp.route('/delete/<int:memo_id>')
@login_required
def delete(memo_id):
    memo = Memo.query.filter_by(id=memo_id, user_id=current_user.id).first_or_404()
    db.session.delete(memo)
    db.session.commit()
    flash('削除しました')
    return redirect(url_for('memo.index'))
