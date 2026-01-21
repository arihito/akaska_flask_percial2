from flask import Blueprint, render_template, redirect, url_for
from models import db, Memo, Favorite
from flask_login import current_user
from sqlalchemy import func

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def public_index():
    raw_memos = db.session.query(
    Memo,
    func.count(Favorite.id).label('like_count')).outerjoin(Favorite, Memo.id == Favorite.memo_id).group_by(Memo.id).order_by(Memo.created_at.desc()).all()
    memos = [
        {"memo": memo, "like_count": like_count}
        for memo, like_count in raw_memos
    ]
    # ---- ログインユーザーのいいね済みID ----
    favorite_memo_ids = []
    if current_user.is_authenticated:
        favorite_memo_ids = [
            f.memo_id for f in Favorite.query.filter_by(user_id=current_user.id)
        ]
    # ---- ランキング用 ----
    raw_top10 = db.session.query(
        Memo,
        func.count(Favorite.id).label("like_count")
    ).outerjoin(Favorite).group_by(Memo.id).order_by(func.count(Favorite.id).desc()).limit(10).all()
    top10 = [
        {"memo": memo, "like_count": like_count}
        for memo, like_count in raw_top10
    ]
    top1 = None
    if top10:
        top1 = top10[0]
    return render_template('public/index.j2', 
        memos=memos, 
        favorite_memo_ids=favorite_memo_ids, 
        top10=top10, 
        top1=top1)

@public_bp.route('/detail/<int:memo_id>')
def detail(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    like_count = Favorite.query.filter_by(memo_id=memo_id).count()
    return render_template(
        'public/detail.j2',
        memo=memo,
        like_count=like_count
    )