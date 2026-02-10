from flask import Blueprint, render_template, request, abort
from models import db, Memo, Favorite, Category
from flask_login import current_user
from sqlalchemy import func
from datetime import date
import markdown
import random

public_bp = Blueprint('public', __name__)
PER_PAGE = 6

@public_bp.app_template_filter("markdown")
def markdown_to_html(text):
    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables"]
    )

@public_bp.route('/')
def public_index():
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(Memo, func.count(Favorite.id).label('like_count')).outerjoin(Favorite, Memo.id == Favorite.memo_id).group_by(Memo.id).order_by(Memo.created_at.desc()).paginate(page=page, per_page=PER_PAGE)
    raw_memos = pagination.items
    total_pages = pagination.pages
    today_seed = date.today().isoformat()
    random.seed(today_seed)
    memos = [{"memo": memo, "like_count": like_count} for memo, like_count in raw_memos]
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
    rand1 = None
    if memos:
        rand1 = random.choice(memos)
    return render_template('public/index.j2', 
        memos=memos,
        page=page,
        total_pages=total_pages, 
        favorite_memo_ids=favorite_memo_ids, 
        top10=top10,
        rand1=rand1)

@public_bp.route('/detail/<int:memo_id>')
def detail(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    like_count = Favorite.query.filter_by(memo_id=memo_id).count()
    raw_top10 = db.session.query(
        Memo,
        func.count(Favorite.id).label("like_count")
    ).outerjoin(Favorite).group_by(Memo.id).order_by(func.count(Favorite.id).desc()).limit(10).all()
    top10 = [
        {"memo": memo, "like_count": like_count}
        for memo, like_count in raw_top10
    ]
    return render_template(
        'public/detail.j2',
        memo=memo,
        top10=top10,
        like_count=like_count
    )
