from flask import render_template
from app import app
from werkzeug.exceptions import NotFound
from models import db, Memo, Favorite
from sqlalchemy import func

@app.errorhandler(NotFound)
def show_404_page(error):
    # ---- ランキング用 ----
    raw_top10 = db.session.query(
        Memo,
        func.count(Favorite.id).label("like_count")
    ).outerjoin(Favorite).group_by(Memo.id).order_by(func.count(Favorite.id).desc()).limit(10).all()
    top10 = [
        {"memo": memo, "like_count": like_count}
        for memo, like_count in raw_top10
    ]
    msg = error.description
    print('エラー内容:', msg)
    return render_template(
        'errors/404.j2', 
        msg=msg,
        top10=top10), 404
