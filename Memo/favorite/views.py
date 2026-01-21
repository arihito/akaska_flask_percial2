from flask import Blueprint, request, redirect, url_for, flash, jsonify
from models import db, Memo, Favorite
from flask_login import login_required, current_user

# 第一引数がurl_for、第三引数がrender_templateで使用する接頭辞
favorite_bp = Blueprint('favorite', __name__, url_prefix='/favorite')

@favorite_bp.route("/add/<int:memo_id>", methods=["POST"])
@login_required
def add(memo_id):
    fav = Favorite(user_id=current_user.id, memo_id=memo_id)
    db.session.add(fav)
    db.session.commit()
    like_count = Favorite.query.filter_by(memo_id=memo_id).count()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(liked=True, like_count=like_count)
    return redirect(url_for("public.public_index"))

@favorite_bp.route("/remove/<int:memo_id>", methods=["POST"])
@login_required
def remove_favorite(memo_id):
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        memo_id=memo_id
    ).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
    like_count = Favorite.query.filter_by(memo_id=memo_id).count()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(liked=False, like_count=like_count)
    return redirect(url_for("public.public_index"))