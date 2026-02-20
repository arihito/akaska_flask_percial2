from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
from forms import AdminLoginForm
from flask_wtf import FlaskForm
from flask_mail import Message
from models import db, User
import stripe

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
        elif current_user.check_admin_password(form.admin_password.data):
            session['is_admin_authenticated'] = True
            flash('管理者としてログインしました', 'secondary')
            return redirect(url_for('admin.index'))
        else:
            flash('管理者パスワードが正しくありません', 'secondary')

    return render_template('admin/login.j2', form=form)


@admin_bp.route('/')
@admin_required
def index():
    users = User.query.order_by(User.id).all()
    form = FlaskForm()
    return render_template('admin/index.j2', users=users, form=form)


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
    db.session.commit()

    if user.is_admin:
        msg = Message(
            subject='【メモアプリ】管理者申請が承認されました',
            recipients=[user.email],
        )
        msg.body = (
            f"{user.username} 様\n\n"
            f"管理者申請が承認されました。\n"
            f"以下のページから決済手続きを行い、管理者ログインしてください。\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"決済ページ: {url_for('admin.payment', _external=True)}\n"
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
    flash('決済が完了しました。管理者用のログインパスワードをご登録のメールアドレスにお送りしますので、しばらくお待ちください。', 'secondary')
    return redirect(url_for('admin.login'))


@admin_bp.route('/payment/cancel')
@login_required
def payment_cancel():
    flash('決済がキャンセルされました', 'secondary')
    return redirect(url_for('admin.payment'))


@admin_bp.route('/logout')
@login_required
def logout():
    session.pop('is_admin_authenticated', None)
    flash('管理者からログアウトしました', 'secondary')
    return redirect(url_for('memo.index'))


######## テストプレビュー：admin/mail-preview
@admin_bp.route("/mail-preview")
@login_required
def mail_preview():

    admin_url = url_for('admin.index', _external=True)

    return render_template(
        "mail/admin_apply.j2",
        user=current_user,
        admin_url=admin_url
    )
