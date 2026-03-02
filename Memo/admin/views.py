import math
import os
import re
from datetime import datetime, timezone, date, timedelta
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request
from flask_login import login_required, current_user
from forms import AdminLoginForm
from flask_wtf import FlaskForm
from flask_mail import Message
from models import db, User, ThumbnailConfig, Memo, Favorite, Category, memo_categories, FixedPage, AppLog
from werkzeug.utils import secure_filename
from sqlalchemy import func
import stripe
import json
from pathlib import Path

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _build_attr_dist(column, labels_order=None):
    """指定カラムの値ごとのユーザー数（NULL/空文字除外）を返す。"""
    rows = db.session.query(column, func.count(User.id))\
        .filter(column.isnot(None))\
        .filter(column != '')\
        .group_by(column)\
        .all()
    total = sum(c for _, c in rows)
    if total == 0:
        return []
    data_map = {v: c for v, c in rows}
    result = []
    seen = set()
    if labels_order:
        for label in labels_order:
            c = data_map.get(label, 0)
            if c > 0:
                result.append({'label': label, 'count': c, 'pct': round(c / total * 100, 1)})
                seen.add(label)
        for v, c in rows:
            if v not in seen and c > 0:
                result.append({'label': v, 'count': c, 'pct': round(c / total * 100, 1)})
    else:
        result = [{'label': v, 'count': c, 'pct': round(c / total * 100, 1)} for v, c in rows]
    return result


def _check_ai_rate_limit(key, limit=5):
    """セッションベースの1日あたりAI機能使用回数チェック。
    本日の使用回数が limit 以内であれば True（カウントアップ）、超過なら False を返す。
    スーパーアドミンは制限なし。
    """
    if _is_super_admin():
        return True
    today = date.today().isoformat()
    session_key = f'ai_rate_{key}'
    entry = session.get(session_key, {'date': '', 'count': 0})
    if entry['date'] != today:
        entry = {'date': today, 'count': 0}
    if entry['count'] >= limit:
        return False
    entry['count'] += 1
    session[session_key] = entry
    session.modified = True
    return True


def _is_super_admin():
    """スーパーアドミン判定（ポイント・時間制限なし）。"""
    return current_user.email == current_app.config.get('MAIL_USERNAME')


def _check_ai_points(cost: int):
    """AIポイント残量チェック。スーパーアドミンは常にTrue。不足時は False を返す（消費はしない）。"""
    if _is_super_admin():
        return True
    return (current_user.admin_points or 0) >= cost


def _consume_ai_points(cost: int):
    """AIポイントを消費してDBに保存する。スーパーアドミンは消費しない。"""
    if _is_super_admin():
        return
    current_user.admin_points = max(0, (current_user.admin_points or 0) - cost)
    db.session.commit()


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


@admin_bp.context_processor
def inject_admin_docs():
    """全管理テンプレートにサイドバーモーダル用のMarkdown変数・pt/残時間を注入"""
    from flask_login import current_user as cu
    admin_points = 0
    remaining_seconds = None
    remaining_h = 0
    remaining_m = 0
    is_expiring_soon = False
    is_points_low = False

    is_super_admin = False
    if cu.is_authenticated and cu.is_admin:
        super_admin_email = current_app.config.get('MAIL_USERNAME')
        is_super_admin = (cu.email == super_admin_email)

    if is_super_admin:
        # スーパーアドミンは無制限（∞表示用に特別値をセット）
        return {
            'requirements_definition': get_requirements_definition(),
            'coding_standards': get_coding_standards(),
            'admin_points': None,   # None = 無制限
            'remaining_h': None,    # None = 無制限
            'remaining_m': 0,
            'is_expiring_soon': False,
            'is_points_low': False,
            'is_super_admin': True,
        }

    if cu.is_authenticated and cu.is_admin:
        admin_points = cu.admin_points or 0
        expires = cu.subscription_expires_at
        if expires:
            # SQLiteはnaive datetimeで返すことがあるため、aware化して統一
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            diff = (expires - now).total_seconds()
            if diff > 0:
                remaining_h = int(diff // 3600)
                remaining_m = int((diff % 3600) // 60)
                is_expiring_soon = diff <= 3 * 3600
        is_points_low = admin_points <= 5

    return {
        'requirements_definition': get_requirements_definition(),
        'coding_standards': get_coding_standards(),
        'admin_points': admin_points,
        'remaining_h': remaining_h,
        'remaining_m': remaining_m,
        'is_expiring_soon': is_expiring_soon,
        'is_points_low': is_points_low,
        'is_super_admin': False,
    }


@admin_bp.before_request
def _warn_subscription_low():
    """管理画面の全リクエストで残pt/残時間が僅かなら flash 警告を出す。"""
    # 認証済みページのみ対象（ログイン・支払いページは除外）
    exempt = {'admin.login', 'admin.apply', 'admin.payment',
              'admin.create_checkout_session', 'admin.payment_success',
              'admin.payment_cancel', 'admin.logout'}
    if request.endpoint in exempt:
        return

    if not session.get('is_admin_authenticated'):
        return

    # スーパーアドミンは制限なし
    super_admin_email = current_app.config.get('MAIL_USERNAME')
    if current_user.email == super_admin_email:
        return

    now = datetime.now(timezone.utc)
    expires = current_user.subscription_expires_at
    # SQLiteはnaive datetimeで返すことがあるため、aware化して統一
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    points = current_user.admin_points or 0

    # 期限切れチェック（admin_required より先に走るケースに備えてここでも検出）
    if expires and expires <= now:
        return  # admin_required 側でリダイレクトされるので警告不要

    warn_msgs = []

    # ── 残り時間警告（前回警告した残り時間帯と変わった場合のみ） ──
    if expires:
        remaining_seconds = (expires - now).total_seconds()
        if remaining_seconds <= 3 * 3600:
            remaining_h = int(remaining_seconds // 3600)
            remaining_m = int((remaining_seconds % 3600) // 60)
            # 1分単位で前回と同じなら再表示しない
            time_key = remaining_h * 60 + remaining_m
            if session.get('_admin_warn_time_key') != time_key:
                session['_admin_warn_time_key'] = time_key
                warn_msgs.append(
                    f'管理者アクセスの残り時間が僅かです（残 {remaining_h}時間{remaining_m}分）。'
                    f'必要であれば追加決済で延長できます。'
                )

    # ── ポイント警告（前回警告したpt数と変わった場合のみ） ──
    if points <= 5:
        last_warned_pt = session.get('_admin_warn_pt')
        if last_warned_pt != points:
            session['_admin_warn_pt'] = points
            if points == 0:
                warn_msgs.append(
                    'AIポイントが無くなったため、AI機能は完全に使用できなくなりました。'
                    '必要があれば、改めて決済することで新たに24ptが加算されます。'
                )
            else:
                warn_msgs.append(
                    f'AIポイントが残り僅かです（残 {points}pt）。'
                    f'ポイントが不足するとAI機能は使用できなくなります。'
                )
    else:
        # 5pt超に回復したらフラグをリセット（次に5pt以下になったら再度警告）
        session.pop('_admin_warn_pt', None)

    if warn_msgs:
        # セッションに溜まった同種の警告（warning カテゴリ）を一旦クリアして重複を防ぐ
        flashes = session.get('_flashes', [])
        session['_flashes'] = [(cat, m) for cat, m in flashes if cat != 'warning']
        for msg in warn_msgs:
            flash(msg, 'warning')


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

    # 帯グラフ: ユーザー属性分布
    attr_dist_data = [
        {'key': '性別',    'segs': _build_attr_dist(User.gender,     ['男性', '女性', 'その他'])},
        {'key': '年代',    'segs': _build_attr_dist(User.age_range,  ['0〜10', '10〜20', '20〜30', '30〜40', '40〜50', '50〜60', '60以上'])},
        {'key': '居住地域', 'segs': _build_attr_dist(User.address,   ['東京都', '神奈川県', '埼玉県', '千葉県', 'その他'])},
        {'key': 'ご職業',  'segs': _build_attr_dist(User.occupation, ['学生', '会社員', '自営業', '主婦・主夫', 'その他'])},
    ]

    is_super_admin = current_user.email == super_admin_email

    return render_template('admin/index.j2',
        users=users,
        form=form,
        is_paginate=is_paginate,
        page=page,
        pages=pages,
        total=total,
        super_admin_email=super_admin_email,
        is_super_admin=is_super_admin,
        bar_chart_data=json.dumps(bar_chart_data, ensure_ascii=False),
        pie_category_data=json.dumps(pie_category_data, ensure_ascii=False),
        pie_user_data=json.dumps(pie_user_data, ensure_ascii=False),
        attr_dist_data=attr_dist_data,
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

    try:
        admin_email = current_app.config['MAIL_USERNAME']
        admin_url = url_for('admin.index', _external=True)
        msg = Message(
            subject='【メモアプリ】管理者申請が届きました',
            recipients=[admin_email],
        )
        msg.html = render_template(
            "mail/admin_apply.j2",
            user=current_user,
            admin_url=admin_url
        )
        msg.body = (
            f"管理者申請が届きました。\n\n"
            f"ユーザー名: {current_user.username}\n"
            f"メール: {current_user.email}\n"
            f"ユーザーID: {current_user.id}\n\n"
            f"管理画面: {admin_url}"
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.error('申請メール送信失敗: %s', str(e), exc_info=True)

    flash('管理者申請を送信しました。運営者の承認をお待ちください。', 'secondary')
    return redirect(url_for('admin.login'))



@admin_bp.route('/approve/<int:user_id>', methods=['POST'])
@admin_required
def approve(user_id):
    """管理者承認：is_admin を切り替え、承認時に通知メール送信（スーパーアドミン専用）"""
    super_admin_email = current_app.config.get('MAIL_USERNAME')
    if current_user.email != super_admin_email:
        flash('この操作はスーパーアドミン専用です', 'secondary')
        return redirect(url_for('admin.index'))
    from app import mail
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    user.approved_at = datetime.now(timezone.utc) if user.is_admin else None
    db.session.commit()

    if user.is_admin:
        try:
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
            mail.send(msg)
        except Exception as e:
            current_app.logger.error('承認メール送信失敗: %s', str(e), exc_info=True)
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


def _send_suspend_request_mail(target_user, requester, reason):
    """スーパーadminに一時停止希望メールを送信"""
    from app import mail
    super_admin_email = current_app.config.get('MAIL_USERNAME')
    admin_url = url_for('admin.index', _external=True)
    msg = Message(
        subject=f'【メモアプリ】一時停止希望：{target_user.username}',
        recipients=[super_admin_email],
    )
    msg.html = render_template(
        'mail/admin_suspend_request.j2',
        target_user=target_user,
        requester=requester,
        reason=reason,
        admin_url=admin_url,
    )
    msg.body = (
        f"一時停止希望が届きました。\n\n"
        f"対象ユーザー: {target_user.username}（{target_user.email}）\n"
        f"依頼者: {requester.username}\n"
        f"理由: {reason}\n\n"
        f"管理画面: {admin_url}"
    )
    try:
        mail.send(msg)
    except Exception as e:
        print(f"######## 一時停止希望メール送信失敗: {e} ########")


@admin_bp.route('/ban/<int:user_id>', methods=['POST'])
@admin_required
def ban(user_id):
    """ユーザー一時停止・解除"""
    user = User.query.get_or_404(user_id)
    super_admin_email = current_app.config.get('MAIL_USERNAME')
    if user.email == super_admin_email:
        flash('スーパーアドミンは停止できません', 'secondary')
        return redirect(url_for('admin.index'))

    is_super_admin = current_user.email == super_admin_email

    if is_super_admin:
        # スーパーadmin: 即トグル
        user.is_banned = not user.is_banned
        if not user.is_banned:
            user.suspend_requested = False
            user.suspend_reason = None
        db.session.commit()
        if user.is_banned:
            flash(f'{user.username} を一時停止しました', 'secondary')
        else:
            flash(f'{user.username} の一時停止を解除しました', 'secondary')
    else:
        if user.is_banned:
            # 停止解除（通常adminも即時可）
            user.is_banned = False
            user.suspend_requested = False
            user.suspend_reason = None
            db.session.commit()
            flash(f'{user.username} の一時停止を解除しました', 'secondary')
        elif user.suspend_requested:
            flash(f'{user.username} は既に一時停止希望済みです。スーパーアドミンの承認をお待ちください', 'secondary')
        else:
            # 一時停止希望：理由を保存してメール通知
            reason = request.form.get('suspend_reason', '').strip()
            if not reason:
                flash('停止理由を入力してください', 'secondary')
                return redirect(url_for('admin.index'))
            user.suspend_requested = True
            user.suspend_reason = reason
            db.session.commit()
            _send_suspend_request_mail(user, current_user, reason)
            flash(f'{user.username} への一時停止希望をスーパーアドミンに通知しました', 'secondary')

    return redirect(url_for('admin.index'))


@admin_bp.route('/ban/approve/<int:user_id>', methods=['POST'])
@admin_required
def ban_approve(user_id):
    """スーパーadmin: 一時停止希望を承認して実行"""
    super_admin_email = current_app.config.get('MAIL_USERNAME')
    if current_user.email != super_admin_email:
        flash('この操作はスーパーアドミンのみ可能です', 'secondary')
        return redirect(url_for('admin.index'))
    user = User.query.get_or_404(user_id)
    if not user.suspend_requested:
        flash('一時停止希望が見つかりません', 'secondary')
        return redirect(url_for('admin.index'))
    user.is_banned = True
    user.suspend_requested = False
    user.suspend_reason = None
    db.session.commit()
    flash(f'{user.username} を一時停止しました（承認実行）', 'secondary')
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


@admin_bp.route('/category/ai_suggest', methods=['POST'])
@admin_required
def category_ai_suggest():
    """AJAX: Gemini AI による Flask トレンドカテゴリー名＋配色提案"""
    from flask import jsonify

    if not _check_ai_rate_limit('category_suggest', limit=5):
        return jsonify(status='error', message='本日のAI生成の利用上限（5回）に達しました。明日以降にお試しください'), 429

    _AI_COST_CATEGORY = 2
    if not _check_ai_points(_AI_COST_CATEGORY):
        return jsonify(status='error', message=f'AIポイントが不足しています（必要: {_AI_COST_CATEGORY}pt / 残: {current_user.admin_points or 0}pt）'), 429

    api_key = current_app.config.get('GOOGLE_API_KEY', '')
    if not api_key:
        return jsonify(status='error', message='GOOGLE_API_KEY が未設定です'), 500

    existing = Category.query.all()
    existing_names  = [c.name  for c in existing]
    existing_colors = [c.color for c in existing]

    try:
        from google import genai
        from google.genai.types import GenerateContentConfig
        import json as json_lib

        client = genai.Client(api_key=api_key)

        names_str  = ', '.join(existing_names)  if existing_names  else 'なし'
        colors_str = ', '.join(existing_colors) if existing_colors else 'なし'

        prompt = (
            f"あなたはFlask技術ブログのカテゴリー設計者です。\n"
            f"以下の条件でカテゴリー名と配色を1件提案してください。\n\n"
            f"【条件】\n"
            f"- カテゴリー名: Flaskやバックエンド開発に関連するトレンド技術名（英数字・ハイフン・アンダースコアのみ・12文字以内）\n"
            f"- 既存カテゴリー名（重複不可）: {names_str}\n"
            f"- カラー: HEX形式・#666より暗い色（明度低め）\n"
            f"- 既存カラー（{colors_str}）と視覚的に区別できる配色を選ぶこと\n\n"
            f"【出力形式】\n"
            f'必ず以下のJSONのみを返してください（説明不要）:\n{{"name": "カテゴリー名", "color": "#xxxxxx"}}'
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=GenerateContentConfig(max_output_tokens=128, temperature=0.9),
        )

        text = response.text.strip()
        json_match = re.search(r'\{[^}]+\}', text)
        if not json_match:
            return jsonify(status='error', message='AI応答の解析に失敗しました'), 500

        data  = json_lib.loads(json_match.group())
        name  = re.sub(r'[^A-Za-z0-9\-_]', '', data.get('name', ''))[:12]
        color = data.get('color', '#234466').strip()
        if not re.match(r'^#[0-9a-fA-F]{6}$', color):
            color = '#234466'

        _consume_ai_points(_AI_COST_CATEGORY)
        return jsonify(status='ok', name=name, color=color, remaining_points=current_user.admin_points)

    except Exception as e:
        print(f"######## カテゴリーAI提案失敗: {e} ########")
        return jsonify(status='error', message='AI提案に失敗しました'), 500


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

    # DB と自動同期（新ファイルは 001〜010 のみ visible=True で追加、削除済みは除去）
    existing = {tc.filename: tc for tc in ThumbnailConfig.query.all()}
    file_set = set(all_files)
    for filename in all_files:
        if filename not in existing:
            m = re.match(r'^(\d+)\.', filename)
            num = int(m.group(1)) if m else None
            is_default_visible = (num is not None and 1 <= num <= 10)
            db.session.add(ThumbnailConfig(filename=filename, visible=is_default_visible))
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


@admin_bp.route('/user_thumb/ai_generate', methods=['POST'])
@admin_required
def user_thumb_ai_generate():
    """AJAX: Imagen API によるユーザーサムネイル画像生成（スーパーアドミン専用・有料）"""
    from flask import jsonify
    from utils.ai_thumb_generate import generate_thumb_image

    if not _check_ai_rate_limit('thumb_generate', limit=5):
        return jsonify(status='error', message='本日のAI生成の利用上限（5回）に達しました。明日以降にお試しください'), 429

    _AI_COST_THUMB = 2
    if not _check_ai_points(_AI_COST_THUMB):
        return jsonify(status='error', message=f'AIポイントが不足しています（必要: {_AI_COST_THUMB}pt / 残: {current_user.admin_points or 0}pt）'), 429

    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')

    image_bytes = generate_thumb_image()
    if not image_bytes:
        return jsonify(status='error', message='AI画像生成に失敗しました。APIキーまたはモデルの設定を確認してください'), 500

    # 3桁連番ファイル名を生成
    user_img_dir = os.path.join(current_app.root_path, 'static', 'images', 'user')
    pattern = re.compile(r'^(\d{3})\.')
    max_num = max(
        (int(m.group(1)) for f in os.listdir(user_img_dir) if (m := pattern.match(f))),
        default=0
    )
    filename = f"{max_num + 1:03d}.png"
    file_path = os.path.join(user_img_dir, filename)
    with open(file_path, 'wb') as fp:
        fp.write(image_bytes)

    # ThumbnailConfig に追加（visible=True）
    if not ThumbnailConfig.query.filter_by(filename=filename).first():
        db.session.add(ThumbnailConfig(filename=filename, visible=True))

    # ユーザーへの割付
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.thumbnail = filename

    db.session.commit()

    _consume_ai_points(_AI_COST_THUMB)
    return jsonify(
        status='ok',
        filename=filename,
        url=url_for('static', filename=f'images/user/{filename}'),
        remaining_points=current_user.admin_points,
    )


@admin_bp.route('/analyze', methods=['POST'])
@admin_required
def analyze():
    """最新5件の記事を Gemini AI で翻訳価値スコアリングし、結果をDBに保存してJSONで返す"""
    from utils.ai_translate_score import score_translate_value
    from flask import jsonify

    if not _check_ai_rate_limit('analyze', limit=5):
        return jsonify(status='error', message='本日のAI解析の利用上限（5回）に達しました。明日以降にお試しください'), 429

    _AI_COST_ANALYZE = 6
    if not _check_ai_points(_AI_COST_ANALYZE):
        return jsonify(status='error', message=f'AIポイントが不足しています（必要: {_AI_COST_ANALYZE}pt / 残: {current_user.admin_points or 0}pt）'), 429

    latest_memos = Memo.query.order_by(Memo.created_at.desc()).limit(5).all()
    results = []
    has_error = False

    for memo in latest_memos:
        # 旧形式（information/writing/readability）は再解析させる
        if memo.ai_score and 'translate_score' in memo.ai_score:
            scores = memo.ai_score
        else:
            like_count_val = Favorite.query.filter_by(memo_id=memo.id).count()
            scores = score_translate_value(
                memo.title, memo.content,
                like_count=like_count_val,
                view_count=memo.view_count or 0,
            )
            if scores:
                memo.ai_score = scores
            else:
                scores = {
                    "seo": 0, "tech": 0, "structure": 0, "spread": 0,
                    "translate_score": 0, "translate_verdict": "エラー",
                    "seo_title": "", "keywords": [], "inflow": "低",
                    "translate_reason": "AI解析に失敗しました",
                }
                has_error = True

        like_count = Favorite.query.filter_by(memo_id=memo.id).count()
        results.append({
            'id': memo.id,
            'title': memo.title[:20] + ('...' if len(memo.title) > 20 else ''),
            'like_count': like_count,
            'view_count': memo.view_count or 0,
            'ai_score': scores,
        })

    db.session.commit()  # ai_score の更新を確実にDBへ保存（_consume_ai_points がスーパーアドミンで早期returnする場合でも保証）
    _consume_ai_points(_AI_COST_ANALYZE)
    return jsonify(status='ok', data=results, remaining_points=current_user.admin_points)


@admin_bp.route('/marketing')
@admin_required
def marketing():
    """マーケティング戦略ページ：翻訳スコア済み記事一覧"""
    memos = Memo.query.filter(Memo.ai_score.isnot(None)).all()
    # translate_score キーを持つ記事のみ・降順ソート
    scored = [m for m in memos if m.ai_score and 'translate_score' in m.ai_score]
    scored.sort(key=lambda m: m.ai_score['translate_score'], reverse=True)
    # いいね数を付与
    for m in scored:
        m.like_count = Favorite.query.filter_by(memo_id=m.id).count()
    form = FlaskForm()
    return render_template('admin/marketing.j2', memos=scored, form=form)


@admin_bp.route('/translate/<int:memo_id>', methods=['POST'])
@admin_required
def translate(memo_id):
    """AJAX: Gemini AI による記事英語翻訳（80点以上のみ）"""
    from utils.ai_translate import translate_memo_to_english
    from flask import jsonify

    if not _check_ai_rate_limit('translate', limit=5):
        return jsonify(status='error', message='本日のAI翻訳の利用上限（5回）に達しました。明日以降にお試しください'), 429

    _AI_COST_TRANSLATE = 4
    if not _check_ai_points(_AI_COST_TRANSLATE):
        return jsonify(status='error', message=f'AIポイントが不足しています（必要: {_AI_COST_TRANSLATE}pt / 残: {current_user.admin_points or 0}pt）'), 429

    memo = Memo.query.get_or_404(memo_id)

    # サーバー側でもスコア検証
    if not memo.ai_score or memo.ai_score.get('translate_score', 0) < 80:
        return jsonify(status='error', message='翻訳スコアが80点未満のため翻訳できません'), 400

    result = translate_memo_to_english(memo.title, memo.content)
    if not result:
        return jsonify(status='error', message='AI翻訳に失敗しました。APIキーと利用制限を確認してください'), 500

    # 翻訳結果を ai_score に追記して保存
    updated = dict(memo.ai_score)
    updated['translated_title'] = result['translated_title']
    updated['translated_body']  = result['translated_body']
    memo.ai_score = updated
    db.session.commit()

    _consume_ai_points(_AI_COST_TRANSLATE)
    return jsonify(
        status='ok',
        translated_title=result['translated_title'],
        translated_body=result['translated_body'],
        remaining_points=current_user.admin_points,
    )


@admin_bp.route('/fixed')
@admin_required
def fixed():
    """固定ページ管理一覧"""
    pages = FixedPage.query.order_by(FixedPage.order).all()
    form = FlaskForm()
    fixed_img_dir = os.path.join(current_app.root_path, 'static', 'images', 'fixed')
    images = sorted([
        f for f in os.listdir(fixed_img_dir)
        if os.path.isfile(os.path.join(fixed_img_dir, f))
        and f.lower().endswith(('.jpg', '.jpeg', '.png'))
        and f != 'keyvisual.jpg'
    ])
    return render_template('admin/fixed.j2', pages=pages, form=form, images=images)


@admin_bp.route('/fixed/toggle/<int:page_id>', methods=['POST'])
@admin_required
def fixed_toggle(page_id):
    """固定ページのナビ表示を切り替え"""
    page = FixedPage.query.get_or_404(page_id)
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('不正なリクエストです', 'secondary')
        return redirect(url_for('admin.fixed'))
    page.visible = not page.visible
    db.session.commit()
    status = '表示' if page.visible else '非表示'
    flash(f'「{page.title}」を{status}に変更しました', 'secondary')
    return redirect(url_for('admin.fixed'))


@admin_bp.route('/fixed/toggle-nav-type/<int:page_id>', methods=['POST'])
@admin_required
def fixed_toggle_nav_type(page_id):
    """固定ページのナビ種別を global ↔ footer に切り替え"""
    page = FixedPage.query.get_or_404(page_id)
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('不正なリクエストです', 'secondary')
        return redirect(url_for('admin.fixed'))
    page.nav_type = 'footer' if page.nav_type == 'global' else 'global'
    db.session.commit()
    label = 'フッター' if page.nav_type == 'footer' else 'グローバルナビ'
    flash(f'「{page.title}」を{label}に変更しました', 'secondary')
    return redirect(url_for('admin.fixed'))


@admin_bp.route('/fixed/delete/<int:page_id>', methods=['POST'])
@admin_required
def fixed_delete(page_id):
    """固定ページをDBから削除（テンプレートファイルは残す）"""
    page = FixedPage.query.get_or_404(page_id)
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('不正なリクエストです', 'secondary')
        return redirect(url_for('admin.fixed'))
    title = page.title
    db.session.delete(page)
    db.session.commit()
    flash(f'固定ページ「{title}」をDBから削除しました（テンプレートファイルは残っています）', 'secondary')
    return redirect(url_for('admin.fixed'))


@admin_bp.route('/fixed/edit/<int:page_id>', methods=['POST'])
@admin_required
def fixed_edit(page_id):
    """固定ページのメタデータ（タイトル・要約・画像・順序）を更新"""
    page = FixedPage.query.get_or_404(page_id)
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('不正なリクエストです', 'secondary')
        return redirect(url_for('admin.fixed'))
    page.title = request.form.get('title', page.title).strip()
    page.summary = request.form.get('summary', page.summary or '').strip() or None
    page.image = request.form.get('image', page.image or '').strip() or None
    try:
        page.order = int(request.form.get('order', page.order))
    except (ValueError, TypeError):
        pass
    db.session.commit()
    flash(f'「{page.title}」を更新しました', 'secondary')
    return redirect(url_for('admin.fixed'))


@admin_bp.route('/fixed/reorder', methods=['POST'])
@admin_required
def fixed_reorder():
    """AJAX: 固定ページの表示順を一括更新（セクション内D&D用）"""
    from flask import jsonify
    data = request.get_json(silent=True) or {}
    ids = data.get('ids', [])
    if not ids:
        return jsonify(status='error', message='IDリストが空です'), 400
    for index, page_id in enumerate(ids):
        page = FixedPage.query.get(page_id)
        if page:
            page.order = index
    db.session.commit()
    return jsonify(status='ok')


@admin_bp.route('/fixed/generate', methods=['POST'])
@admin_required
def fixed_generate():
    """AJAX: Gemini AI による固定ページコンテンツ生成"""
    from flask import jsonify
    from utils.ai_fixed_generate import generate_fixed_page

    if not _check_ai_rate_limit('fixed_generate', limit=5):
        return jsonify(status='error', message='本日のAI生成の利用上限（5回）に達しました。明日以降にお試しください'), 429

    _AI_COST_FIXED = 2
    if not _check_ai_points(_AI_COST_FIXED):
        return jsonify(status='error', message=f'AIポイントが不足しています（必要: {_AI_COST_FIXED}pt / 残: {current_user.admin_points or 0}pt）'), 429

    data = request.get_json(silent=True) or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify(status='error', message='タイトルを入力してください'), 400

    existing_keys = [p.key for p in FixedPage.query.all()]
    result = generate_fixed_page(title, existing_keys)
    if not result:
        return jsonify(status='error', message='AI生成に失敗しました。APIキーと利用制限を確認してください'), 500

    # ランダム画像を選択
    fixed_img_dir = os.path.join(current_app.root_path, 'static', 'images', 'fixed')
    images = [
        f for f in os.listdir(fixed_img_dir)
        if os.path.isfile(os.path.join(fixed_img_dir, f))
        and f.lower().endswith(('.jpg', '.jpeg', '.png'))
        and f != 'keyvisual.jpg'
    ]
    import random
    selected_image = random.choice(images) if images else 'refactor.jpg'

    _consume_ai_points(_AI_COST_FIXED)
    return jsonify(status='ok', **result, image=selected_image, remaining_points=current_user.admin_points)


@admin_bp.route('/fixed/random-image')
@admin_required
def fixed_random_image():
    """AJAX: ランダムに画像を返す"""
    from flask import jsonify
    import random
    fixed_img_dir = os.path.join(current_app.root_path, 'static', 'images', 'fixed')
    images = [
        f for f in os.listdir(fixed_img_dir)
        if os.path.isfile(os.path.join(fixed_img_dir, f))
        and f.lower().endswith(('.jpg', '.jpeg', '.png'))
        and f != 'keyvisual.jpg'
    ]
    image = random.choice(images) if images else 'refactor.jpg'
    return jsonify(image=image)


@admin_bp.route('/fixed/create', methods=['POST'])
@admin_required
def fixed_create():
    """AI生成コンテンツをDBに保存しテンプレートファイルを書き出す"""
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('不正なリクエストです', 'secondary')
        return redirect(url_for('admin.fixed'))

    key = request.form.get('key', '').strip()
    title = request.form.get('title', '').strip()
    summary = request.form.get('summary', '').strip() or None
    content = request.form.get('content', '').strip()
    image = request.form.get('image', '').strip() or None
    visible = request.form.get('visible') == 'on'
    redirect_to_memo = request.form.get('redirect_to_memo') == '1'

    if not key or not title or not content:
        flash('必須項目が不足しています', 'secondary')
        return redirect(url_for('admin.fixed'))

    if FixedPage.query.filter_by(key=key).first():
        flash(f'キー「{key}」はすでに使用されています', 'secondary')
        return redirect(url_for('admin.fixed'))

    # .j2 テンプレートファイルを書き出し
    # Markdown内のJinja2メタ文字をエスケープ（コードブロック内の {{ }} {%  %} を安全にする）
    safe_content = (
        content
        .replace('{{', "{{ '{{' }}")
        .replace('}}', "{{ '}}' }}")
        .replace('{%', "{{ '{%' }}")
        .replace('%}', "{{ '%}' }}")
        .replace('{#', "{{ '{#' }}")
        .replace('#}', "{{ '#}' }}")
    )
    template_dir = os.path.join(current_app.root_path, 'templates', 'fixed')
    template_path = os.path.join(template_dir, f'{key}.j2')
    j2_content = (
        '{% extends "fixed/base.j2" %}\n'
        '{% block article_body %}\n'
        '{% set md %}\n'
        + safe_content + '\n'
        '{% endset %}'
        '{{ md | markdown | safe }}\n'
        '{% endblock article_body %}\n'
    )
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(j2_content)
    except Exception as e:
        print(f"######## 固定ページテンプレート書き出し失敗: {e} ########")
        flash('テンプレートファイルの書き出しに失敗しました', 'secondary')
        return redirect(url_for('admin.fixed'))

    max_order = db.session.query(func.max(FixedPage.order)).scalar() or 0
    new_page = FixedPage(
        key=key,
        title=title,
        summary=summary,
        image=image,
        visible=visible,
        order=max_order + 1,
    )
    db.session.add(new_page)
    db.session.commit()

    flash(f'固定ページ「{title}」を作成しました（/fixed/{key}）', 'secondary')
    if redirect_to_memo:
        from urllib.parse import urlencode
        params = urlencode({'title': title, 'body': content, 'summary': summary or ''})
        return redirect(url_for('memo.create') + '?' + params)
    return redirect(url_for('admin.fixed'))


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


# ===================================================
# テスト網羅率ページ
# ===================================================

def _get_ast_coverage_items(filepath, executed_set, missing_set, display_name):
    """AST解析でファイル内のトップレベル関数・メソッド・クラスのカバレッジを取得する。"""
    import ast as _ast
    try:
        source = filepath.read_text(encoding='utf-8')
        tree = _ast.parse(source)
    except (SyntaxError, OSError, UnicodeDecodeError):
        return [], []

    stmt_lines = executed_set | missing_set

    def _calc(node):
        node_lines = stmt_lines & set(range(node.lineno, node.end_lineno + 1))
        cov = node_lines & executed_set
        miss = node_lines & missing_set
        total = len(node_lines)
        pct = int(len(cov) / total * 100) if total else 0
        return {'stmts': total, 'covered': len(cov), 'missing': len(miss), 'pct': pct}

    functions = []
    classes = []
    for node in tree.body:
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            m = _calc(node)
            if m['stmts'] == 0:
                continue
            functions.append({'name': node.name, 'file': display_name, 'line': node.lineno, **m})
        elif isinstance(node, _ast.ClassDef):
            m = _calc(node)
            if m['stmts'] == 0:
                continue
            classes.append({'name': node.name, 'file': display_name, 'line': node.lineno, **m})
            for child in node.body:
                if isinstance(child, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                    cm = _calc(child)
                    if cm['stmts'] == 0:
                        continue
                    functions.append({
                        'name': f"{node.name}.{child.name}",
                        'file': display_name,
                        'line': child.lineno,
                        **cm,
                    })
    return functions, classes


def _parse_coverage_json(coverage_json_path):
    """coverage.json を読み込んでテンプレート用データに変換する。"""
    import json as _json
    from datetime import datetime
    if not coverage_json_path.exists():
        return None
    with open(coverage_json_path, encoding='utf-8') as f:
        data = _json.load(f)

    # 除外するファイルパターン（ノイズになるファイル）
    EXCLUDE_PATTERNS = ['__init__', 'seed.py', 'dev_print.py', 'factories/']
    project_root = coverage_json_path.parent

    totals = data['totals']
    files = []
    all_functions = []
    all_classes = []
    for name, info in sorted(data['files'].items(), key=lambda x: x[0]):
        if any(p in name for p in EXCLUDE_PATTERNS):
            continue
        pct = info['summary']['percent_covered_display']
        stmts = info['summary']['num_statements']
        covered = info['summary']['covered_lines']
        missing = info['summary']['missing_lines']
        display_name = name.replace('\\', '/')
        files.append({
            'name': display_name,
            'pct': int(pct),
            'stmts': stmts,
            'covered': covered,
            'missing': missing,
        })
        # AST解析でfunction/class coverage取得
        filepath = project_root / name
        executed_set = set(info.get('executed_lines', []))
        missing_set = set(info.get('missing_lines', []))
        funcs, classes = _get_ast_coverage_items(filepath, executed_set, missing_set, display_name)
        all_functions.extend(funcs)
        all_classes.extend(classes)

    mtime = coverage_json_path.stat().st_mtime
    last_run = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

    return {
        'total_pct': int(totals['percent_covered_display']),
        'total_stmts': totals['num_statements'],
        'total_covered': totals['covered_lines'],
        'total_missing': totals['missing_lines'],
        'files': files,
        'functions': sorted(all_functions, key=lambda x: x['name']),
        'classes': sorted(all_classes, key=lambda x: x['name']),
        'last_run': last_run,
    }


@admin_bp.route('/coverage')
@login_required
def coverage():
    coverage_json_path = Path(current_app.root_path) / 'coverage.json'
    coverage_data = _parse_coverage_json(coverage_json_path)
    return render_template('admin/coverage.j2', coverage=coverage_data)


@admin_bp.route('/coverage/run', methods=['POST'])
@login_required
def coverage_run():
    """pytest を実行して coverage.json を生成し、結果を JSON で返す。"""
    import subprocess, sys
    python = sys.executable
    project_root = Path(current_app.root_path)
    try:
        result = subprocess.run(
            [python, '-m', 'pytest', '--cov=.', '--cov-report=json', '-q', '--tb=no'],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=120,
        )
        coverage_json_path = project_root / 'coverage.json'
        coverage_data = _parse_coverage_json(coverage_json_path)
        if coverage_data is None:
            return {'ok': False, 'error': 'coverage.json が生成されませんでした'}, 500
        passed = result.returncode == 0
        return {
            'ok': True,
            'passed': passed,
            'coverage': coverage_data,
        }
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'タイムアウト（120秒）'}, 500
    except Exception as e:
        return {'ok': False, 'error': str(e)}, 500


# ===== ログ可視化 =====

def _parse_log_line(line):
    """1行のログを辞書にパースする。パース失敗時は None を返す。"""
    pattern = r'^\[(.+?)\] (\w+) \[(.+?)\] (.+)$'
    m = re.match(pattern, line.strip())
    if not m:
        return None
    return {
        'datetime': m.group(1),
        'level': m.group(2).upper(),
        'module': m.group(3),
        'message': m.group(4),
    }


@admin_bp.route('/logs')
@admin_required
def logs():
    days = int(request.args.get('days', 1))
    if days not in (1, 3, 7):
        days = 1

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = AppLog.query.filter(AppLog.created_at >= cutoff)\
        .order_by(AppLog.created_at.desc()).all()

    entries = [
        {
            'datetime': row.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'level': row.level,
            'module': row.module,
            'message': row.message,
        }
        for row in rows
    ]

    summary = {
        'error':   sum(1 for e in entries if e['level'] == 'ERROR'),
        'warning': sum(1 for e in entries if e['level'] == 'WARNING'),
        'info':    sum(1 for e in entries if e['level'] == 'INFO'),
        'total':   len(entries),
    }

    return render_template('admin/logs.j2', logs=entries, days=days, summary=summary)
