import math
import os
import re
from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request
from flask_login import login_required, current_user
from forms import AdminLoginForm
from flask_wtf import FlaskForm
from flask_mail import Message
from models import db, User, ThumbnailConfig, Memo, Favorite, Category, memo_categories
from werkzeug.utils import secure_filename
from sqlalchemy import func
import stripe
import json
from pathlib import Path

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """管理者セッション認証デコレータ"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin_authenticated') or not current_user.is_admin:
            session.pop('is_admin_authenticated', None)
            flash('管理者としてログインしてください', 'secondary')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# マークダウンのコード取得
BASE_DIR = Path(__file__).resolve().parent.parent
def get_markdown_content(relative_path: str, start_marker: str = None, end_marker: str = None):
    """
    Markdownファイルを取得する共通関数

    :param relative_path: プロジェクトルートからの相対パス
    :param start_marker: 部分取得開始マーカー（省略可）
    :param end_marker: 部分取得終了マーカー（省略可）
    :return: Markdown文字列
    """
    md_path = BASE_DIR / relative_path
    if not md_path.exists():
        return f"{relative_path} が見つかりません。"
    content = md_path.read_text(encoding="utf-8")
    # マーカー未指定なら全文返却
    if not start_marker or not end_marker:
        return content.strip()
    start = content.find(start_marker)
    end = content.find(end_marker)
    if start == -1 or end == -1:
        return "指定されたセクションが見つかりません。"
    start += len(start_marker)
    return content[start:end].strip()

# 要件定義
def get_requirements_definition():
    return get_markdown_content(
        "README.md",
        start_marker="<!-- START_TERM -->",
        end_marker="<!-- END_TERM -->"
    )

# コーディング規約
def get_coding_standards():
    return get_markdown_content("static/docs/CODING_STANDARDS.md")


@admin_bp.route('/login', methods=['GET', 'POST'])
@login_required
def login():
    # 既に管理者認証済みなら管理画面へ
    if session.get('is_admin_authenticated'):
        return redirect(url_for('admin.index'))

    form = AdminLoginForm()

    if form.validate_on_submit():
        if not current_user.is_admin:
            flash('管理者権限がありません', 'secondary')
        else:
            is_super_admin = current_user.email == current_app.config.get('MAIL_USERNAME')
            password_ok = current_user.check_admin_password(form.admin_password.data)
            if is_super_admin and not password_ok:
                password_ok = current_user.check_password(form.admin_password.data)

            if password_ok:
                session['is_admin_authenticated'] = True
                flash('管理者としてログインしました', 'secondary')
                return redirect(url_for('admin.index'))
            else:
                flash('管理者パスワードが正しくありません', 'secondary')

    return render_template('admin/login.j2', form=form)


@admin_bp.route('/')
@admin_required
def index():
    per_page = 10
    page = request.args.get('page', 1, type=int)
    total = User.query.count()
    pages = math.ceil(total / per_page)
    offset = (page - 1) * per_page
    is_paginate = pages > 1
    users = User.query.order_by(User.id).limit(per_page).offset(offset).all()
    requirements_definition = get_requirements_definition()
    coding_standards = get_coding_standards()
    form = FlaskForm()
    super_admin_email = current_app.config.get('MAIL_USERNAME')

    # ---- チャート用データ ----
    # 棒グラフ: 最新5件の記事
    latest_memos = Memo.query.order_by(Memo.created_at.desc()).limit(5).all()
    bar_chart_data = []
    for memo in latest_memos:
        like_count = Favorite.query.filter_by(memo_id=memo.id).count()
        bar_chart_data.append({
            'id': memo.id,
            'title': memo.title[:20] + ('...' if len(memo.title) > 20 else ''),
            'like_count': like_count,
            'view_count': memo.view_count or 0,
            'ai_score': memo.ai_score,
        })

    # 円グラフ1: カテゴリー分布（全記事）
    cat_dist = db.session.query(
        Category.name,
        Category.color,
        func.count(memo_categories.c.memo_id).label('count')
    ).join(memo_categories, Category.id == memo_categories.c.category_id) \
     .group_by(Category.id) \
     .order_by(func.count(memo_categories.c.memo_id).desc()) \
     .all()
    pie_category_data = [
        {'name': name, 'color': color, 'count': count}
        for name, color, count in cat_dist
    ]

    # 円グラフ2: ユーザー別投稿数 TOP5
    user_dist = db.session.query(
        User.username,
        func.count(Memo.id).label('count')
    ).join(Memo, User.id == Memo.user_id) \
     .group_by(User.id) \
     .order_by(func.count(Memo.id).desc()) \
     .limit(5) \
     .all()
    pie_user_data = [
        {'name': name, 'count': count}
        for name, count in user_dist
    ]

    return render_template('admin/index.j2',
        users=users,
        form=form,
        requirements_definition=requirements_definition,
        coding_standards=coding_standards,
        is_paginate=is_paginate,
        page=page,
        pages=pages,
        total=total,
        super_admin_email=super_admin_email,
        bar_chart_data=json.dumps(bar_chart_data, ensure_ascii=False),
        pie_category_data=json.dumps(pie_category_data, ensure_ascii=False),
        pie_user_data=json.dumps(pie_user_data, ensure_ascii=False),
    )


@admin_bp.route('/apply', methods=['POST'])
@login_required
def apply():
    """管理者申請：運営者にメール送信"""
    if current_user.is_admin:
        flash('すでに管理者権限があります', 'secondary')
        return redirect(url_for('admin.login'))
    if current_user.is_applied:
        flash('すでに申請済みです。承認をお待ちください', 'secondary')
        return redirect(url_for('admin.login'))

    from app import mail
    current_user.is_applied = True
    current_user.applied_at = datetime.now(timezone.utc)
    db.session.commit()

    admin_email = current_app.config['MAIL_USERNAME']
    msg = Message(
        subject='【メモアプリ】管理者申請が届きました',
        recipients=[admin_email],
    )

    admin_url=url_for('admin.index', _external=True)
    # HTMLテンプレート
    msg.html = render_template(
        "mail/admin_apply.j2",
        user=current_user,
        admin_url=admin_url
    )

    # スパム対応プレーンテキスト
    msg.body = f"""
    管理者申請が届きました。

    ユーザー名: {current_user.username}
    メール: {current_user.email}
    ユーザーID: {current_user.id}

    管理画面:
    {admin_url}
    """

    try:
        mail.send(msg)
    except Exception as e:
        print(f"######## 申請メール送信失敗: {e} ########")

    flash('管理者申請を送信しました。運営者の承認をお待ちください。', 'secondary')
    return redirect(url_for('admin.login'))



@admin_bp.route('/approve/<int:user_id>', methods=['POST'])
@admin_required
def approve(user_id):
    """管理者承認：is_admin を切り替え、承認時に通知メール送信"""
    from app import mail
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    user.approved_at = datetime.now(timezone.utc) if user.is_admin else None
    db.session.commit()

    if user.is_admin:
        payment_url = url_for('admin.payment', _external=True)
        msg = Message(
            subject='【メモアプリ】管理者申請が承認されました',
            recipients=[user.email],
        )
        msg.html = render_template(
            "mail/admin_approve.j2",
            user=user,
            payment_url=payment_url,
        )
        msg.body = (
            f"{user.username} 様\n\n"
            f"管理者申請が承認されました。\n"
            f"以下のページから決済手続きを行い、管理者ログインしてください。\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"決済ページ: {payment_url}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
        )
        try:
            mail.send(msg)
        except Exception as e:
            print(f"######## 承認通知メール送信失敗: {e} ########")
        flash(f'{user.username} を承認し、通知メールを送信しました', 'secondary')
    else:
        flash(f'{user.username} の管理者権限を取り消しました', 'secondary')

    return redirect(url_for('admin.index'))


@admin_bp.route('/payment')
@login_required
def payment():
    if not current_user.is_admin:
        flash('管理者の承認が必要です', 'secondary')
        return redirect(url_for('admin.login'))
    form = FlaskForm()
    return render_template('admin/payment.j2', form=form)


@admin_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    price = current_app.config['ADMIN_PLAN_PRICE']
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'jpy',
                    'product_data': {
                        'name': '管理者アクセスプラン（10日間）',
                    },
                    'unit_amount': price,
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        metadata={'user_id': str(current_user.id)},
        success_url=url_for('admin.payment_success', _external=True),
        cancel_url=url_for('admin.payment_cancel', _external=True),
    )
    return redirect(checkout_session.url, code=303)


@admin_bp.route('/payment/success')
@login_required
def payment_success():
    flash('決済が完了しました。あなたはスーパーユーザーです！管理者用のログインパスワードをご登録のメールアドレスにお送りしますので、しばらくお待ちください。', 'secondary')
    return redirect(url_for('admin.login'))


@admin_bp.route('/payment/cancel')
@login_required
def payment_cancel():
    flash('決済がキャンセルされました', 'secondary')
    return redirect(url_for('admin.payment'))


@admin_bp.route('/ban/<int:user_id>', methods=['POST'])
@admin_required
def ban(user_id):
    """ユーザー一時停止・解除"""
    user = User.query.get_or_404(user_id)
    super_admin_email = current_app.config.get('MAIL_USERNAME')
    if user.email == super_admin_email:
        flash('スーパーアドミンは停止できません', 'secondary')
        return redirect(url_for('admin.index'))
    user.is_banned = not user.is_banned
    db.session.commit()

    if user.is_banned:
        flash(f'{user.username} を一時停止しました', 'secondary')
    else:
        flash(f'{user.username} の一時停止を解除しました', 'secondary')

    return redirect(url_for('admin.index'))


@admin_bp.route('/category', methods=['GET', 'POST'])
@admin_required
def category():
    from models import Category
    form = FlaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = request.form.get('name', '').strip()
        color = request.form.get('color', '').strip()
        if Category.query.filter_by(name=name).first():
            flash(f'カテゴリー「{name}」はすでに存在します', 'secondary')
        else:
            new_cat = Category(name=name, color=color)
            db.session.add(new_cat)
            db.session.commit()
            flash(f'カテゴリー「{name}」を追加しました', 'secondary')
        return redirect(url_for('admin.category'))
    categories = Category.query.order_by(Category.id).all()
    return render_template('admin/category.j2', categories=categories, form=form)


@admin_bp.route('/category/delete/<int:cat_id>', methods=['POST'])
@admin_required
def category_delete(cat_id):
    from models import Category
    cat = Category.query.get_or_404(cat_id)
    if cat.memos:
        flash(f'カテゴリー「{cat.name}」は{len(cat.memos)}件の記事で使用中のため削除できません', 'secondary')
        return redirect(url_for('admin.category'))
    db.session.delete(cat)
    db.session.commit()
    flash(f'カテゴリー「{cat.name}」を削除しました', 'secondary')
    return redirect(url_for('admin.category'))


@admin_bp.route('/user_thumb')
@admin_required
def user_thumb():
    users = User.query.order_by(User.id).all()
    form = FlaskForm()

    # static/images/user/ の全ファイルをスキャン
    EXCLUDE = {'default.png', 'images.png'}
    user_img_dir = os.path.join(current_app.root_path, 'static', 'images', 'user')
    all_files = sorted([
        f for f in os.listdir(user_img_dir)
        if os.path.isfile(os.path.join(user_img_dir, f)) and f not in EXCLUDE
    ])

    # DB と自動同期（新ファイルは visible=True で追加、削除済みは除去）
    existing = {tc.filename: tc for tc in ThumbnailConfig.query.all()}
    file_set = set(all_files)
    for filename in all_files:
        if filename not in existing:
            db.session.add(ThumbnailConfig(filename=filename, visible=True))
    for filename, tc in existing.items():
        if filename not in file_set:
            db.session.delete(tc)
    db.session.commit()

    thumb_configs = ThumbnailConfig.query.filter(
        ThumbnailConfig.filename.in_(file_set)
    ).order_by(ThumbnailConfig.filename).all()

    return render_template('admin/user_thumb.j2', users=users, form=form, thumb_configs=thumb_configs)


@admin_bp.route('/user_thumb/upload', methods=['POST'])
@admin_required
def user_thumb_upload():
    """サムネイル画像アップロード（3桁自動連番でファイル保存・旧ファイルは削除しない）"""
    user_id = request.form.get('user_id', type=int)
    file = request.files.get('file')

    if not file or file.filename == '':
        flash('ファイルが選択されていません', 'secondary')
        return redirect(url_for('admin.user_thumb'))

    # 3桁連番ファイル名を生成（ディレクトリ内の最大番号 + 1）
    user_img_dir = os.path.join(current_app.root_path, 'static', 'images', 'user')
    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    pattern = re.compile(r'^(\d{3})\.')
    max_num = max(
        (int(m.group(1)) for f in os.listdir(user_img_dir) if (m := pattern.match(f))),
        default=0
    )
    filename = f"{max_num + 1:03d}{ext}"
    file.save(os.path.join(user_img_dir, filename))

    # ThumbnailConfig に追加（visible=True）
    if not ThumbnailConfig.query.filter_by(filename=filename).first():
        db.session.add(ThumbnailConfig(filename=filename, visible=True))

    # ユーザーが選択されている場合のみ割付
    if user_id:
        user = User.query.get_or_404(user_id)
        user.thumbnail = filename
        db.session.commit()
        flash(f'{user.username} さんのサムネイルを更新しました（{filename}）', 'secondary')
    else:
        db.session.commit()
        flash(f'サムネイルを追加しました（{filename}）', 'secondary')

    return redirect(url_for('admin.user_thumb'))


@admin_bp.route('/user_thumb/visibility', methods=['POST'])
@admin_required
def thumbnail_visibility_update():
    """サムネイル表示設定の一括更新・削除処理"""
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('不正なリクエストです', 'secondary')
        return redirect(url_for('admin.user_thumb'))

    # ── 削除処理 ──
    delete_files = set(request.form.getlist('delete_thumbs'))
    deleted_count = 0
    if delete_files:
        for tc in ThumbnailConfig.query.filter(ThumbnailConfig.filename.in_(delete_files)).all():
            # 使用中ユーザーを default.png に自動リセット
            User.query.filter_by(thumbnail=tc.filename).update({'thumbnail': 'default.png'})
            # 物理ファイル削除
            file_path = os.path.join(current_app.root_path, 'static', 'images', 'user', tc.filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"######## サムネイルファイル削除失敗: {e} ########")
            db.session.delete(tc)
            deleted_count += 1

    # ── 表示設定更新（削除対象は除外） ──
    checked = set(request.form.getlist('visible_thumbs')) - delete_files
    for tc in ThumbnailConfig.query.all():
        if tc.filename not in delete_files:
            tc.visible = tc.filename in checked

    db.session.commit()

    if deleted_count:
        flash(f'サムネイルを {deleted_count} 件削除し、表示設定を更新しました', 'secondary')
    else:
        flash('サムネイルの表示設定を更新しました', 'secondary')
    return redirect(url_for('admin.user_thumb'))


@admin_bp.route('/analyze', methods=['POST'])
@admin_required
def analyze():
    """最新5件の記事をGemini AIでスコアリングし、結果をDBに保存してJSONで返す"""
    from utils.ai_score import analyze_memo_quality
    from flask import jsonify

    latest_memos = Memo.query.order_by(Memo.created_at.desc()).limit(5).all()
    results = []
    has_error = False

    for memo in latest_memos:
        if memo.ai_score:
            scores = memo.ai_score
        else:
            scores = analyze_memo_quality(memo.title, memo.content)
            if scores:
                memo.ai_score = scores
            else:
                scores = {"information": 0, "writing": 0, "readability": 0}
                has_error = True

        like_count = Favorite.query.filter_by(memo_id=memo.id).count()
        results.append({
            'id': memo.id,
            'title': memo.title[:20] + ('...' if len(memo.title) > 20 else ''),
            'like_count': like_count,
            'view_count': memo.view_count or 0,
            'ai_score': scores,
        })

    db.session.commit()
    return jsonify(status='ok', data=results)


@admin_bp.route('/logout')
@login_required
def logout():
    session.pop('is_admin_authenticated', None)
    flash('管理者からログアウトしました', 'secondary')
    return redirect(url_for('memo.index'))


######## テストプレビュー：admin_apply/preview
@admin_bp.route("/mail-apply")
@login_required
def mail_apply():

    admin_url = url_for('admin.index', _external=True)

    return render_template(
        "mail/admin_apply.j2",
        user=current_user,
        admin_url=admin_url
    )


######## テストプレビュー：admin_approve/preview
@admin_bp.route("/mail-approve")
@login_required
def mail_approve():

    payment_url = url_for('admin.payment', _external=True)

    return render_template(
        "mail/admin_approve.j2",
        user=current_user,
        payment_url=payment_url
    )
