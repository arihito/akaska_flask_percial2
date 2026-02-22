from flask import Blueprint, render_template, abort
from models import db, Memo, Favorite, FixedPage
from sqlalchemy import func

fixed_bp = Blueprint('fixed', __name__, url_prefix='/fixed')


@fixed_bp.route("/<page_name>")
def static_page(page_name):
    page = FixedPage.query.filter_by(key=page_name).first()
    if not page:
        abort(404)
    # ---- ランキング用 ----
    raw_top10 = db.session.query(
        Memo,
        func.count(Favorite.id).label("like_count")
    ).outerjoin(Favorite).group_by(Memo.id).order_by(func.count(Favorite.id).desc()).limit(10).all()
    top10 = [
        {"memo": memo, "like_count": like_count}
        for memo, like_count in raw_top10
    ]
    return render_template(
        f'fixed/{page_name}.j2',
        page_title=page.title,
        key_visual=f'/static/images/fixed/{page.image or page_name + ".jpg"}',
        top10=top10
    )
