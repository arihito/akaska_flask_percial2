import os
import requests
from flask import Blueprint, render_template, request, jsonify
from werkzeug.exceptions import NotFound
from models import db, Memo, Favorite
from sqlalchemy import func

error_bp = Blueprint('error', __name__, url_prefix='/error')

@error_bp.errorhandler(NotFound)
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

@error_bp.route('/translate', methods=['POST'])
def translate():
    text = request.json.get('text')
    if not text:
        return jsonify({'error': 'no text'}), 400

    res = requests.post(
        'https://api-free.deepl.com/v2/translate',
        data={
            'auth_key': os.environ['DEEPL_API_KEY'],
            'text': text,
            'target_lang': 'JA'
        }
    )
    return jsonify(res.json())
