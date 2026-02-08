from flask import Blueprint, render_template, abort
from models import db, Memo, Favorite
from sqlalchemy import func

fixed_bp = Blueprint('fixed', __name__, url_prefix='/fixed')

STATIC_PAGES = {
    'refactor' : '環境構築',
    'crud' : 'CRUD',
    'paging' : 'ページング',
    'upload' : 'ファイルアップロード',
    'drop' : 'ドラッグ&ドロップ',
    'htmx' : '非同期',
    'oauth' : 'Googleログイン',
    'jwt' : 'JWT認証',
    'twofactor' : '二段階認証',
    'stripe' : 'カード決済',
    'i18n' : '多言語設定',
    'deploy' : 'デプロイ',
    'help' : 'ヘルプ',
    'terms' : '利用規約',
    'policy' : 'プライバシーポリシー',
    'legal' : '特定商取引法に基づく表記',
    'disclaimer' : '免責事項',
    'copyright' : '著作権・引用について'
}

@fixed_bp.route("/<page_name>")
def static_page(page_name):
    title = STATIC_PAGES.get(page_name)
    print(title)
    if not title:
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
        page_title=title,
        key_visual=f'/static/images/fixed/{page_name}.jpg',
        top10=top10
    )
